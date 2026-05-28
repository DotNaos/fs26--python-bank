from typing import Any


ASSET_ACCOUNTS = {"central_bank", "credit_assets"}

ACCOUNT_OUTPUT_NAMES = {
    "central_bank": "zentralbankkonto",
    "customer_liabilities": "verpflichtungskonto",
    "credit_assets": "kreditkonto_aktiva",
    "income": "einnahmenkonto",
}


def round_money(value: float) -> float:
    return round(float(value), 2)


def output_amount(value: float | int) -> float | int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return round_money(value)


def create_ledger() -> dict[str, Any]:
    return {
        "central_bank": 0.0,
        "customer_liabilities": 0.0,
        "credit_assets": 0.0,
        "income": 0.0,
        "entries": [],
    }


def record_entry(
    bank_state: dict[str, Any],
    timestamp: str,
    event_type: str,
    reference: str,
    debit_account: str,
    debit_amount: float,
    credit_account: str,
    credit_amount: float,
) -> None:
    ledger = bank_state["ledger"]
    posted_debit_amount = round_money(debit_amount)
    posted_credit_amount = round_money(credit_amount)

    post_debit(ledger, debit_account, posted_debit_amount)
    post_credit(ledger, credit_account, posted_credit_amount)

    ledger["entries"].append(
        {
            "zeitstempel": timestamp,
            "vorgang": event_type,
            "referenz": reference,
            "soll_konto": ACCOUNT_OUTPUT_NAMES[debit_account],
            "soll_betrag": output_amount(debit_amount),
            "haben_konto": ACCOUNT_OUTPUT_NAMES[credit_account],
            "haben_betrag": output_amount(credit_amount),
        }
    )


def post_debit(ledger: dict[str, Any], account: str, amount: float) -> None:
    if account in ASSET_ACCOUNTS:
        ledger[account] = round_money(ledger[account] + amount)
    else:
        ledger[account] = round_money(ledger[account] - amount)


def post_credit(ledger: dict[str, Any], account: str, amount: float) -> None:
    if account in ASSET_ACCOUNTS:
        ledger[account] = round_money(ledger[account] - amount)
    else:
        ledger[account] = round_money(ledger[account] + amount)


def balance_is_valid(bank_state: dict[str, Any], tolerance: float = 0.01) -> bool:
    ledger = bank_state["ledger"]
    assets = ledger["central_bank"] + ledger["credit_assets"]
    liabilities_and_income = ledger["customer_liabilities"] + ledger["income"]
    return abs(round_money(assets - liabilities_and_income)) <= tolerance


def export_ledger(bank_state: dict[str, Any]) -> dict[str, Any]:
    ledger = bank_state["ledger"]
    return {
        "zentralbankkonto": round_money(ledger["central_bank"]),
        "verpflichtungskonto": round_money(ledger["customer_liabilities"]),
        "kreditkonto_aktiva": round_money(ledger["credit_assets"]),
        "einnahmenkonto": round_money(ledger["income"]),
        "buchungen": ledger["entries"],
    }
