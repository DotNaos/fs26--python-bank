import pytest

from python_bank.accounts import (
    book_incoming_payment,
    close_account,
    create_bank_state,
    execute_outgoing_transfer,
    open_account,
)
from python_bank.credits import grant_credit, repay_credit
from python_bank.ledger import balance_is_valid, record_entry


def test_iban_generation_uses_moodle_format():
    bank_state = create_bank_state()

    first = open_account(
        bank_state,
        {
            "name": "Anna Muster",
            "adresse": "Bahnhofstrasse 1, 7000 Chur",
            "geburtsdatum": "1990-05-15",
        },
        "2026-01-02T09:00:01Z",
    )
    second = open_account(
        bank_state,
        {
            "name": "Beat Keller",
            "adresse": "Grabenstrasse 12, 7000 Chur",
            "geburtsdatum": "1985-08-22",
        },
        "2026-01-02T09:00:02Z",
    )

    assert first == "CH00007620000000000011"
    assert second == "CH00007620000000000022"


def test_credit_grant_repayment_and_ledger_balance():
    bank_state = create_bank_state()
    bank_state["current_date"] = "2026-01-02"
    iban = open_account(
        bank_state,
        {
            "name": "Anna Muster",
            "adresse": "Bahnhofstrasse 1, 7000 Chur",
            "geburtsdatum": "1990-05-15",
        },
        "2026-01-02T09:00:01Z",
    )

    book_incoming_payment(bank_state, iban, 5000, "2026-01-02T10:00:00Z", "2026-01-02T08:00:02Z")
    assert grant_credit(bank_state, iban, 1000, "2026-01-15T14:00:00Z", "2026-01-15T08:00:02Z") is True
    assert repay_credit(bank_state, iban, 250, "2026-01-20T09:00:00Z", "2026-01-20T08:00:02Z") is True

    account = bank_state["accounts"][iban]
    assert account["balance"] == 5500.0
    assert account["credit_balance"] == 750.0
    assert balance_is_valid(bank_state) is True


def test_blocked_account_rejects_outgoing_transfer():
    bank_state = create_bank_state()
    iban = open_account(
        bank_state,
        {
            "name": "Anna Muster",
            "adresse": "Bahnhofstrasse 1, 7000 Chur",
            "geburtsdatum": "1990-05-15",
        },
        "2026-01-02T09:00:01Z",
    )
    bank_state["accounts"][iban]["status"] = "gesperrt"

    result = execute_outgoing_transfer(
        bank_state,
        iban,
        "IT60X0542811101000000123456",
        100,
        "2026-01-03T10:00:00Z",
        "2026-01-03T08:00:02Z",
    )

    assert result is False
    assert bank_state["meta"]["rejected_transactions"] == 1
    assert bank_state["accounts"][iban]["transactions"][-1]["status"] == "abgelehnt"
    assert bank_state["accounts"][iban]["transactions"][-1]["grund"] == "Konto gesperrt"


def test_invalid_payment_amounts_raise_errors():
    bank_state = create_bank_state()
    iban = open_account(
        bank_state,
        {
            "name": "Anna Muster",
            "adresse": "Bahnhofstrasse 1, 7000 Chur",
            "geburtsdatum": "1990-05-15",
        },
        "2026-01-02T09:00:01Z",
    )

    with pytest.raises(ValueError):
        book_incoming_payment(bank_state, iban, 0, "2026-01-02T10:00:00Z", "2026-01-02T08:00:02Z")
    with pytest.raises(ValueError):
        execute_outgoing_transfer(
            bank_state,
            iban,
            "IT60X0542811101000000123456",
            -100,
            "2026-01-03T10:00:00Z",
            "2026-01-03T08:00:02Z",
        )


def test_repayment_caps_overpayment_after_penalty_interest():
    bank_state = create_bank_state()
    bank_state["current_date"] = "2026-01-02"
    iban = open_account(
        bank_state,
        {
            "name": "Anna Muster",
            "adresse": "Bahnhofstrasse 1, 7000 Chur",
            "geburtsdatum": "1990-05-15",
        },
        "2026-01-02T09:00:01Z",
    )

    book_incoming_payment(bank_state, iban, 1000, "2026-01-02T10:00:00Z", "2026-01-02T08:00:02Z")
    grant_credit(bank_state, iban, 1000, "2026-01-15T14:00:00Z", "2026-01-15T08:00:02Z")
    repay_credit(bank_state, iban, 900, "2026-01-20T09:00:00Z", "2026-01-20T08:00:02Z")

    account = bank_state["accounts"][iban]
    account["credit"]["penalty_balance"] = 40.0
    account["credit_balance"] = 140.0
    record_entry(
        bank_state,
        "2026-01-21T08:00:02Z",
        "strafzinsen",
        f"Strafzinsen {iban}",
        "credit_assets",
        40.0,
        "income",
        40.0,
    )

    assert repay_credit(bank_state, iban, 1000, "2026-01-22T09:00:00Z", "2026-01-22T08:00:02Z") is True
    assert account["balance"] == 710.0
    assert account["credit_balance"] == 0.0
    assert account["credit"]["active"] is False
    assert account["transactions"][-1]["betrag"] == -140.0
    assert bank_state["ledger"]["credit_assets"] == 0.0
    assert balance_is_valid(bank_state) is True


def test_account_close_requires_zero_balance_and_zero_credit():
    bank_state = create_bank_state()
    iban = open_account(
        bank_state,
        {
            "name": "Anna Muster",
            "adresse": "Bahnhofstrasse 1, 7000 Chur",
            "geburtsdatum": "1990-05-15",
        },
        "2026-01-02T09:00:01Z",
    )
    book_incoming_payment(bank_state, iban, 100, "2026-01-02T10:00:00Z", "2026-01-02T08:00:02Z")

    assert close_account(bank_state, iban, "2026-01-03T10:00:00Z") is False
    assert bank_state["accounts"][iban]["transactions"][-1]["typ"] == "konto_schliessen"
    assert bank_state["accounts"][iban]["transactions"][-1]["status"] == "abgelehnt"

