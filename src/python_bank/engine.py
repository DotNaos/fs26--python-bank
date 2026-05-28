import argparse
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .accounts import (
    book_incoming_payment,
    charge_quarterly_fees,
    close_account,
    create_bank_state,
    execute_outgoing_transfer,
    get_account,
    open_account,
    update_customer_data,
)
from .credits import (
    check_blocked_account_after_incoming_payment,
    grant_credit,
    process_daily_penalty_interest,
    process_monthly_credit_work,
    repay_credit,
)
from .storage import load_transactions, save_outputs


TRANSACTION_ORDER = {
    "konto_eroeffnen": 0,
    "ueberweisung_ein": 1,
    "zeit": 2,
    "kredit_antrag": 3,
    "kredit_rueckzahlung": 3,
    "daten_aendern": 4,
    "konto_schliessen": 4,
    "ueberweisung_aus": 5,
}

DEFAULT_TRANSACTION_PATH = Path("data/reference/transaktionen")
DEFAULT_OUTPUT_DIR = Path("output/reference-run")


def run_bank_simulation(transaction_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    transactions = load_transactions(transaction_path)
    bank_state = create_bank_state()
    bank_state["input_transactions"] = transactions

    process_transactions(transactions, bank_state)
    save_outputs(bank_state, output_dir)
    return bank_state


def process_transactions(transactions: list[dict[str, Any]], bank_state: dict[str, Any]) -> None:
    for date, daily_transactions in sorted(group_transactions_by_date(transactions).items()):
        process_daily_batch(bank_state, date, daily_transactions)


def group_transactions_by_date(transactions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for transaction in transactions:
        grouped[transaction_date(transaction)].append(transaction)
    return grouped


def transaction_date(transaction: dict[str, Any]) -> str:
    if transaction["typ"] == "zeit":
        return transaction["datum"]
    return parse_timestamp(transaction["zeitstempel"]).date().isoformat()


def process_daily_batch(bank_state: dict[str, Any], date: str, transactions: list[dict[str, Any]]) -> None:
    bank_state["current_date"] = date
    booking_index = 2

    for transaction in sort_daily_batch(transactions):
        ledger_time = ledger_time_from_transaction(date, transaction, booking_index)
        booking_index = execute_transaction(bank_state, transaction, ledger_time, booking_index)
        bank_state["meta"]["processed_transactions"] += 1


def sort_daily_batch(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        transactions,
        key=lambda transaction: (
            TRANSACTION_ORDER.get(transaction["typ"], 99),
            parse_timestamp(transaction["zeitstempel"]),
        ),
    )


def execute_transaction(
    bank_state: dict[str, Any],
    transaction: dict[str, Any],
    ledger_time: str,
    booking_index: int,
) -> int:
    transaction_type = transaction["typ"]

    if transaction_type == "konto_eroeffnen":
        open_account(bank_state, transaction["kunde"], transaction["zeitstempel"])
    elif transaction_type == "ueberweisung_ein":
        book_incoming_payment(
            bank_state,
            transaction["ziel_iban"],
            transaction["betrag"],
            transaction["zeitstempel"],
            ledger_time,
            transaction.get("referenz", ""),
        )
        account = get_account(bank_state, transaction["ziel_iban"])
        check_blocked_account_after_incoming_payment(bank_state, account, transaction["zeitstempel"], ledger_time)
        booking_index += 2
    elif transaction_type == "zeit":
        booking_index = process_periodic_work(bank_state, transaction["datum"], booking_index)
    elif transaction_type == "kredit_antrag":
        grant_credit(bank_state, transaction["kunden_iban"], transaction["betrag"], transaction["zeitstempel"], ledger_time)
        booking_index += 4
    elif transaction_type == "kredit_rueckzahlung":
        repay_credit(bank_state, transaction["kunden_iban"], transaction["betrag"], transaction["zeitstempel"], ledger_time)
        booking_index += 2
    elif transaction_type == "daten_aendern":
        iban = transaction.get("kunden_iban", transaction.get("iban"))
        update_customer_data(bank_state, iban, transaction.get("neue_daten", {}), transaction["zeitstempel"])
    elif transaction_type == "konto_schliessen":
        iban = transaction.get("kunden_iban", transaction.get("iban"))
        close_account(bank_state, iban, transaction["zeitstempel"])
    elif transaction_type == "ueberweisung_aus":
        source_iban = transaction.get("quell_iban", transaction.get("von_iban"))
        target_iban = transaction.get("ziel_iban", transaction.get("nach_iban"))
        execute_outgoing_transfer(
            bank_state,
            source_iban,
            target_iban,
            transaction["betrag"],
            transaction["zeitstempel"],
            ledger_time,
            transaction.get("referenz", ""),
        )
        booking_index += 2
    else:
        bank_state["meta"]["unknown_transactions"] += 1
        raise ValueError(f"Unknown transaction type: {transaction_type}")

    return booking_index


def process_periodic_work(bank_state: dict[str, Any], date: str, start_index: int) -> int:
    current_date = datetime.strptime(date, "%Y-%m-%d").date()
    current_month = (current_date.year, current_date.month)
    current_quarter = (current_date.year, (current_date.month - 1) // 3)
    is_first_day_in_month = bank_state["previous_month"] is not None and bank_state["previous_month"] != current_month
    is_first_day_in_quarter = bank_state["previous_quarter"] is not None and bank_state["previous_quarter"] != current_quarter
    index = start_index

    if is_first_day_in_month:
        index = process_monthly_credit_work(bank_state, date, index)
    if is_first_day_in_quarter:
        index = charge_quarterly_fees(bank_state, date, index)
    index = process_daily_penalty_interest(bank_state, date, index)

    bank_state["previous_month"] = current_month
    bank_state["previous_quarter"] = current_quarter
    return index


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def booking_timestamp(date: str, index: int) -> str:
    minute = index // 60
    second = index % 60
    return f"{date}T08:{minute:02d}:{second:02d}Z"


def ledger_time_from_transaction(date: str, transaction: dict[str, Any], index: int) -> str:
    transaction_type = transaction["typ"]
    if transaction_type == "zeit":
        return booking_timestamp(date, index)

    timestamp = parse_timestamp(transaction["zeitstempel"])
    extra_seconds = 2 if transaction_type == "kredit_antrag" else 1
    ledger_time = datetime.strptime(
        f"{date}T08:{timestamp.minute:02d}:{timestamp.second:02d}Z",
        "%Y-%m-%dT%H:%M:%SZ",
    )
    return (ledger_time + timedelta(seconds=extra_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the FS26 Python Bank simulation.")
    parser.add_argument("transactions", nargs="?", default=None)
    parser.add_argument("output", nargs="?", default=None)
    parser.add_argument("--transaction-file", dest="transaction_file", default=None)
    parser.add_argument("--output-dir", dest="output_dir", default=None)
    return parser


def has_explicit_paths(args: argparse.Namespace) -> bool:
    return any((args.transaction_file, args.transactions, args.output_dir, args.output))


def prompt_for_paths() -> tuple[Path, Path] | None:
    print("FS26 Python Bank")
    print("================")
    print("1. Run bundled reference data")
    print("2. Run custom transaction path")
    print("3. Exit")
    choice = input("Choose an option [1]: ").strip() or "1"

    if choice == "3":
        return None
    if choice == "1":
        output = input(f"Output directory [{DEFAULT_OUTPUT_DIR}]: ").strip()
        return DEFAULT_TRANSACTION_PATH, Path(output) if output else DEFAULT_OUTPUT_DIR
    if choice == "2":
        transaction_path = input("Transaction file or directory: ").strip()
        if not transaction_path:
            raise SystemExit("Transaction path is required.")
        output = input(f"Output directory [{DEFAULT_OUTPUT_DIR}]: ").strip()
        return Path(transaction_path), Path(output) if output else DEFAULT_OUTPUT_DIR

    raise SystemExit(f"Unknown option: {choice}")


def print_run_summary(bank_state: dict[str, Any]) -> None:
    print("Simulation completed.")
    print(f"Processed transactions: {bank_state['meta']['processed_transactions']}")
    print(f"Customer transaction entries: {sum(len(account['transactions']) for account in bank_state['accounts'].values())}")
    print(f"Ledger entries: {len(bank_state['ledger']['entries'])}")


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    if not has_explicit_paths(args):
        selected_paths = prompt_for_paths()
        if selected_paths is None:
            print("No simulation run.")
            return 0
        transaction_path, output_dir = selected_paths
    else:
        transaction_path = args.transaction_file or args.transactions or DEFAULT_TRANSACTION_PATH
        output_dir = args.output_dir or args.output or DEFAULT_OUTPUT_DIR

    bank_state = run_bank_simulation(transaction_path, output_dir)
    print_run_summary(bank_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
