from typing import Any

from .ledger import create_ledger, output_amount, record_entry, round_money


BANK_CLEARING = "00762"
QUARTERLY_ACCOUNT_FEE = 25.0


def create_bank_state() -> dict[str, Any]:
    return {
        "current_date": None,
        "previous_month": None,
        "previous_quarter": None,
        "next_account_number": 1,
        "accounts": {},
        "ledger": create_ledger(),
        "meta": {
            "processed_transactions": 0,
            "rejected_transactions": 0,
            "unknown_transactions": 0,
            "warnings": [],
        },
    }


def generate_iban(bank_state: dict[str, Any]) -> str:
    account_number = bank_state["next_account_number"]
    bank_state["next_account_number"] += 1
    number = f"{account_number:012d}"
    return f"CH00{BANK_CLEARING}{number}{number[-1]}"


def open_account(bank_state: dict[str, Any], customer_data: dict[str, Any], timestamp: str) -> str:
    iban = generate_iban(bank_state)
    account = {
        "iban": iban,
        "customer": dict(customer_data),
        "balance": 0.0,
        "credit_balance": 0.0,
        "status": "aktiv",
        "transactions": [],
        "credit": {
            "principal": 0.0,
            "remaining_principal": 0.0,
            "penalty_balance": 0.0,
            "active": False,
            "paid_months": 0,
            "last_payment_date": None,
            "written_off": False,
        },
    }
    store_account_transaction(account, timestamp, "konto_eroeffnen", 0.0)
    bank_state["accounts"][iban] = account
    return iban


def get_account(bank_state: dict[str, Any], iban: str) -> dict[str, Any]:
    try:
        return bank_state["accounts"][iban]
    except KeyError as exc:
        raise ValueError(f"Account not found: {iban}") from exc


def store_account_transaction(
    account: dict[str, Any],
    timestamp: str,
    event_type: str,
    amount: float,
    status: str = "ausgefuehrt",
    reason: str | None = None,
) -> None:
    entry = {
        "zeitstempel": timestamp,
        "typ": event_type,
        "betrag": output_amount(amount),
        "saldo_nachher": round_money(account["balance"]),
        "status": status,
    }
    if reason:
        entry["grund"] = reason
    account["transactions"].append(entry)
    if status == "abgelehnt":
        account["balance_before_rejected_transaction"] = round_money(account["balance"])


def book_incoming_payment(
    bank_state: dict[str, Any],
    iban: str,
    amount: float,
    timestamp: str,
    ledger_time: str,
    reference: str = "",
) -> None:
    account = get_account(bank_state, iban)
    posted_amount = round_money(amount)
    if posted_amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    account["balance"] = round_money(account["balance"] + posted_amount)
    store_account_transaction(account, timestamp, "ueberweisung_ein", amount)
    record_entry(
        bank_state,
        ledger_time,
        "ueberweisung_ein",
        reference,
        "central_bank",
        amount,
        "customer_liabilities",
        amount,
    )


def execute_outgoing_transfer(
    bank_state: dict[str, Any],
    source_iban: str,
    target_iban: str,
    amount: float,
    timestamp: str,
    ledger_time: str,
    reference: str = "",
) -> bool:
    account = get_account(bank_state, source_iban)
    posted_amount = round_money(amount)
    if posted_amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    if account["status"] != "aktiv":
        reject_transaction(account, timestamp, "ueberweisung_aus", -posted_amount, "Konto gesperrt", bank_state)
        return False
    if account["balance"] < posted_amount:
        reject_transaction(account, timestamp, "ueberweisung_aus", -posted_amount, "Deckung nicht ausreichend", bank_state)
        return False

    account["balance"] = round_money(account["balance"] - posted_amount)
    store_account_transaction(account, timestamp, "ueberweisung_aus", -posted_amount)

    if target_iban in bank_state["accounts"]:
        target_account = bank_state["accounts"][target_iban]
        target_account["balance"] = round_money(target_account["balance"] + posted_amount)
        from .credits import add_seconds

        store_account_transaction(target_account, add_seconds(timestamp, 1), "ueberweisung_ein", posted_amount)
        return True

    record_entry(
        bank_state,
        ledger_time,
        "ueberweisung_aus",
        reference,
        "customer_liabilities",
        posted_amount,
        "central_bank",
        posted_amount,
    )
    return True


def reject_transaction(
    account: dict[str, Any],
    timestamp: str,
    event_type: str,
    amount: float,
    reason: str,
    bank_state: dict[str, Any],
) -> None:
    store_account_transaction(account, timestamp, event_type, amount, "abgelehnt", reason)
    bank_state["meta"]["rejected_transactions"] += 1


def update_customer_data(bank_state: dict[str, Any], iban: str, new_data: dict[str, Any], timestamp: str) -> None:
    account = get_account(bank_state, iban)
    account["customer"].update(new_data)
    store_account_transaction(account, timestamp, "daten_aendern", 0.0)


def close_account(bank_state: dict[str, Any], iban: str, timestamp: str) -> bool:
    account = get_account(bank_state, iban)
    if account["balance"] != 0 or account["credit_balance"] != 0:
        reject_transaction(account, timestamp, "konto_schliessen", 0.0, "Saldo oder Kredit offen", bank_state)
        return False
    account["status"] = "geschlossen"
    store_account_transaction(account, timestamp, "konto_schliessen", 0.0)
    return True


def charge_quarterly_fees(bank_state: dict[str, Any], date: str, start_index: int) -> int:
    from .credits import add_seconds
    from .engine import booking_timestamp

    index = start_index
    for account in bank_state["accounts"].values():
        if account["status"] == "geschlossen":
            continue
        account["balance"] = round_money(account["balance"] - QUARTERLY_ACCOUNT_FEE)
        timestamp = booking_timestamp(date, index)
        store_account_transaction(account, add_seconds(timestamp, -1), "kontogebuehr", -QUARTERLY_ACCOUNT_FEE)
        record_entry(
            bank_state,
            timestamp,
            "kontogebuehr",
            f"Kontogebuehr Q {account['iban']}",
            "customer_liabilities",
            QUARTERLY_ACCOUNT_FEE,
            "income",
            QUARTERLY_ACCOUNT_FEE,
        )
        index += 2
    return index


def refresh_credit_balance(account: dict[str, Any]) -> None:
    credit = account["credit"]
    account["credit_balance"] = round_money(credit["remaining_principal"] + credit["penalty_balance"])


def export_account(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "konto_iban": account["iban"],
        "kunde": account["customer"],
        "kontostand": round_money(account["balance"]),
        "kredit_stand": round_money(account["credit_balance"]),
        "status": account["status"],
        "transaktionen": account["transactions"],
    }
