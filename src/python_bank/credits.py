from datetime import datetime, timedelta
from typing import Any

from .accounts import get_account, refresh_credit_balance, reject_transaction, store_account_transaction
from .ledger import record_entry, round_money


MIN_CREDIT = 1000.0
MAX_CREDIT = 15000.0
CREDIT_FEE = 250.0
ANNUAL_CREDIT_INTEREST = 0.15
ANNUAL_PENALTY_INTEREST = 0.30
CREDIT_TERM_MONTHS = 12


def add_seconds(timestamp: str, seconds: int) -> str:
    base = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return (base + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_distance(start: str, end: str) -> int:
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month


def monthly_principal_payment(account: dict[str, Any]) -> float:
    credit = account["credit"]
    payment = round_money(credit["principal"] / CREDIT_TERM_MONTHS)
    return round_money(min(payment, credit["remaining_principal"]))


def grant_credit(
    bank_state: dict[str, Any],
    iban: str,
    amount: float,
    timestamp: str,
    ledger_time: str,
) -> bool:
    account = get_account(bank_state, iban)
    credit = account["credit"]
    requested_amount = amount
    amount = round_money(amount)

    if not MIN_CREDIT <= amount <= MAX_CREDIT:
        reject_transaction(account, timestamp, "kredit_antrag", 0.0, "Kreditbetrag ungueltig", bank_state)
        return False
    if credit["active"] and credit["remaining_principal"] + credit["penalty_balance"] > 0.0:
        reject_transaction(account, timestamp, "kredit_antrag", 0.0, "Kredit laeuft bereits", bank_state)
        return False

    credit.update(
        {
            "principal": amount,
            "remaining_principal": amount,
            "penalty_balance": 0.0,
            "active": True,
            "paid_months": 0,
            "last_payment_date": bank_state["current_date"],
            "written_off": False,
        }
    )

    account["balance"] = round_money(account["balance"] + amount)
    store_account_transaction(account, add_seconds(timestamp, 1), "kredit_auszahlung", requested_amount)
    record_entry(
        bank_state,
        ledger_time,
        "kredit_auszahlung",
        f"Kredit {iban}",
        "credit_assets",
        requested_amount,
        "customer_liabilities",
        requested_amount,
    )

    account["balance"] = round_money(account["balance"] - CREDIT_FEE)
    store_account_transaction(account, add_seconds(timestamp, 3), "kredit_gebuehr", -CREDIT_FEE)
    record_entry(
        bank_state,
        add_seconds(ledger_time, 2),
        "kredit_gebuehr",
        f"Kreditgebuehr {iban}",
        "customer_liabilities",
        CREDIT_FEE,
        "income",
        CREDIT_FEE,
    )
    refresh_credit_balance(account)
    return True


def repay_credit(
    bank_state: dict[str, Any],
    iban: str,
    amount: float,
    timestamp: str,
    ledger_time: str,
) -> bool:
    account = get_account(bank_state, iban)
    credit = account["credit"]
    requested_amount = amount
    amount = round_money(amount)
    if not credit["active"] or amount <= 0:
        reject_transaction(account, timestamp, "kredit_rueckzahlung", -amount, "Rueckzahlung nicht moeglich", bank_state)
        return False

    penalty_payment = round_money(min(amount, credit["penalty_balance"]))
    remaining_amount = round_money(amount - penalty_payment)
    principal_payment = round_money(min(remaining_amount, credit["remaining_principal"]))
    payment = round_money(penalty_payment + principal_payment)
    if payment <= 0 or account["balance"] < payment:
        reject_transaction(account, timestamp, "kredit_rueckzahlung", -amount, "Rueckzahlung nicht moeglich", bank_state)
        return False

    credit["penalty_balance"] = round_money(credit["penalty_balance"] - penalty_payment)
    credit["remaining_principal"] = round_money(credit["remaining_principal"] - principal_payment)
    account["balance"] = round_money(account["balance"] - payment)
    credit["last_payment_date"] = bank_state["current_date"]
    if credit["remaining_principal"] <= 0 and credit["penalty_balance"] <= 0:
        credit["active"] = False
    refresh_credit_balance(account)
    displayed_payment = -requested_amount if round_money(requested_amount) == payment else -payment
    store_account_transaction(account, timestamp, "kredit_rueckzahlung", displayed_payment)
    if penalty_payment > 0:
        record_entry(
            bank_state,
            ledger_time,
            "kredit_rueckzahlung",
            f"Rueckzahlung Strafzins {iban}",
            "customer_liabilities",
            requested_amount if round_money(requested_amount) == penalty_payment else penalty_payment,
            "credit_assets",
            requested_amount if round_money(requested_amount) == penalty_payment else penalty_payment,
        )
    if principal_payment > 0:
        record_entry(
            bank_state,
            ledger_time,
            "kredit_rueckzahlung",
            f"Rueckzahlung {iban}",
            "customer_liabilities",
            requested_amount if round_money(requested_amount) == principal_payment else principal_payment,
            "credit_assets",
            requested_amount if round_money(requested_amount) == principal_payment else principal_payment,
        )
    return True


def check_blocked_account_after_incoming_payment(
    bank_state: dict[str, Any],
    account: dict[str, Any],
    timestamp: str,
    ledger_time: str,
) -> None:
    credit = account["credit"]
    if account["status"] != "gesperrt" or not credit["active"] or credit["written_off"]:
        return
    payment = monthly_principal_payment(account)
    if account["balance"] < payment:
        return

    account["balance"] = round_money(account["balance"] - payment)
    credit["remaining_principal"] = round_money(max(0.0, credit["remaining_principal"] - payment))
    credit["paid_months"] += 1
    credit["last_payment_date"] = bank_state["current_date"]
    account["status"] = "aktiv"
    refresh_credit_balance(account)
    store_account_transaction(account, timestamp, "kredit_amortisation", -payment)
    record_entry(
        bank_state,
        ledger_time,
        "kredit_amortisation",
        "Nachzahlung",
        "customer_liabilities",
        payment,
        "credit_assets",
        payment,
    )


def charge_credit_interest(bank_state: dict[str, Any], account: dict[str, Any], date: str, index: int) -> int:
    from .engine import booking_timestamp

    credit = account["credit"]
    if credit["remaining_principal"] <= 0:
        return index
    interest = round_money((credit["remaining_principal"] + credit["penalty_balance"]) * ANNUAL_CREDIT_INTEREST / 12.0)
    if interest <= 0:
        return index
    account["balance"] = round_money(account["balance"] - interest)
    timestamp = booking_timestamp(date, index)
    store_account_transaction(account, add_seconds(timestamp, -1), "kredit_zinsen", -interest)
    record_entry(
        bank_state,
        timestamp,
        "kredit_zinsen",
        f"Kreditzinsen {account['iban']}",
        "customer_liabilities",
        interest,
        "income",
        interest,
    )
    return index + 2


def process_credit_amortization(bank_state: dict[str, Any], account: dict[str, Any], date: str, index: int) -> int:
    from .engine import booking_timestamp

    credit = account["credit"]
    if credit["remaining_principal"] <= 0 or account["status"] == "gesperrt":
        return index + 1 if account["status"] == "gesperrt" and credit["remaining_principal"] > 0 else index
    payment = monthly_principal_payment(account)
    timestamp = booking_timestamp(date, index)
    if account["balance"] < payment:
        account["status"] = "gesperrt"
        store_account_transaction(account, add_seconds(timestamp, -1), "konto_gesperrt", 0.0, reason="Amortisation nicht moeglich")
        return index + 1

    account["balance"] = round_money(account["balance"] - payment)
    credit["remaining_principal"] = round_money(credit["remaining_principal"] - payment)
    credit["paid_months"] += 1
    credit["last_payment_date"] = date
    if credit["remaining_principal"] <= 0 and credit["penalty_balance"] <= 0:
        credit["active"] = False
    refresh_credit_balance(account)
    store_account_transaction(account, add_seconds(timestamp, -1), "kredit_amortisation", -payment)
    record_entry(
        bank_state,
        timestamp,
        "kredit_amortisation",
        f"Amortisation {account['iban']}",
        "customer_liabilities",
        payment,
        "credit_assets",
        payment,
    )
    return index + 2


def charge_penalty_interest(bank_state: dict[str, Any], account: dict[str, Any], date: str, index: int) -> int:
    from .engine import booking_timestamp

    credit = account["credit"]
    outstanding = credit["remaining_principal"] + credit["penalty_balance"]
    if outstanding <= 0:
        return index
    penalty = round_money(outstanding * ANNUAL_PENALTY_INTEREST / 365.0)
    credit["penalty_balance"] = round_money(credit["penalty_balance"] + penalty)
    refresh_credit_balance(account)
    timestamp = booking_timestamp(date, index)
    store_account_transaction(account, add_seconds(timestamp, -1), "strafzinsen", -penalty)
    record_entry(
        bank_state,
        timestamp,
        "strafzinsen",
        f"Strafzinsen {account['iban']}",
        "credit_assets",
        penalty,
        "income",
        penalty,
    )
    return index + 2


def check_credit_writeoff(bank_state: dict[str, Any], account: dict[str, Any], date: str, index: int) -> int:
    from .engine import booking_timestamp

    credit = account["credit"]
    if not credit["active"] or credit["written_off"] or not credit["last_payment_date"]:
        return index
    if month_distance(credit["last_payment_date"], date) < 6:
        return index
    outstanding = round_money(credit["remaining_principal"] + credit["penalty_balance"])
    if outstanding <= 0:
        return index
    timestamp = booking_timestamp(date, index)
    record_entry(
        bank_state,
        timestamp,
        "kredit_abschreibung",
        f"Abschreibung {account['iban']}",
        "income",
        outstanding,
        "credit_assets",
        outstanding,
    )
    credit["remaining_principal"] = 0.0
    credit["penalty_balance"] = 0.0
    credit["active"] = False
    credit["written_off"] = True
    refresh_credit_balance(account)
    store_account_transaction(account, add_seconds(timestamp, -1), "kredit_abschreibung", 0.0, reason="Abschreibung nach 6 Monaten ohne Zahlung")
    return index + 2


def process_monthly_credit_work(bank_state: dict[str, Any], date: str, start_index: int) -> int:
    index = start_index
    for account in bank_state["accounts"].values():
        credit = account["credit"]
        if credit["active"] and not credit["written_off"]:
            index = charge_credit_interest(bank_state, account, date, index)
            index = process_credit_amortization(bank_state, account, date, index)
            index = check_credit_writeoff(bank_state, account, date, index)
    return index


def process_daily_penalty_interest(bank_state: dict[str, Any], date: str, start_index: int) -> int:
    index = start_index
    for account in bank_state["accounts"].values():
        credit = account["credit"]
        if account["status"] == "gesperrt" and credit["active"] and not credit["written_off"]:
            index = charge_penalty_interest(bank_state, account, date, index)
    return index
