from python_bank.engine import (
    group_transactions_by_date,
    ledger_time_from_transaction,
    main,
    run_bank_simulation,
    sort_daily_batch,
)
from python_bank.storage import read_json


def test_daily_batch_order_matches_moodle_update():
    transactions = [
        {"typ": "ueberweisung_aus", "zeitstempel": "2026-01-02T10:00:00Z"},
        {"typ": "zeit", "zeitstempel": "2026-01-02T08:00:00Z", "datum": "2026-01-02"},
        {"typ": "kredit_antrag", "zeitstempel": "2026-01-02T09:00:00Z"},
        {"typ": "ueberweisung_ein", "zeitstempel": "2026-01-02T11:00:00Z"},
        {"typ": "konto_eroeffnen", "zeitstempel": "2026-01-02T12:00:00Z"},
        {"typ": "daten_aendern", "zeitstempel": "2026-01-02T07:00:00Z"},
    ]

    assert [tx["typ"] for tx in sort_daily_batch(transactions)] == [
        "konto_eroeffnen",
        "ueberweisung_ein",
        "zeit",
        "kredit_antrag",
        "daten_aendern",
        "ueberweisung_aus",
    ]


def test_grouping_uses_time_transaction_date():
    grouped = group_transactions_by_date(
        [
            {"typ": "zeit", "zeitstempel": "2026-01-02T23:59:00Z", "datum": "2026-01-03"},
            {"typ": "ueberweisung_ein", "zeitstempel": "2026-01-02T10:00:00Z"},
        ]
    )

    assert sorted(grouped) == ["2026-01-02", "2026-01-03"]


def test_ledger_time_rolls_minute_overflow():
    transaction = {
        "typ": "ueberweisung_ein",
        "zeitstempel": "2026-01-02T10:59:59Z",
    }

    assert ledger_time_from_transaction("2026-01-02", transaction, 0) == "2026-01-02T09:00:00Z"


def test_small_simulation_writes_expected_files(tmp_path):
    transactions = tmp_path / "transactions.json"
    transactions.write_text(
        """
[
  {
    "typ": "konto_eroeffnen",
    "zeitstempel": "2026-01-02T09:00:01Z",
    "kunde": {"name": "Anna Muster", "adresse": "Bahnhofstrasse 1, 7000 Chur", "geburtsdatum": "1990-05-15"}
  },
  {"typ": "zeit", "zeitstempel": "2026-01-02T08:00:00Z", "datum": "2026-01-02"},
  {
    "typ": "ueberweisung_ein",
    "zeitstempel": "2026-01-02T10:00:01Z",
    "ziel_iban": "CH00007620000000000011",
    "betrag": 500.0,
    "waehrung": "CHF",
    "absender_iban": "IT60X0542811101000000123456",
    "referenz": "Initial payment"
  }
]
""",
        encoding="utf-8",
    )

    state = run_bank_simulation(transactions, tmp_path / "out")

    assert state["meta"]["processed_transactions"] == 3
    assert (tmp_path / "out" / "bankkonten.json").exists()
    assert (tmp_path / "out" / "zusammenfassung.json").exists()
    assert (tmp_path / "out" / "konten" / "anna_muster.json").exists()
    assert read_json(tmp_path / "out" / "zusammenfassung.json")["anzahl_kunden"] == 1


def test_no_argument_cli_uses_interactive_menu(monkeypatch, tmp_path, capsys):
    output_dir = tmp_path / "menu-run"
    answers = iter(["1", str(output_dir)])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert main([]) == 0

    captured = capsys.readouterr()
    assert "FS26 Python Bank" in captured.out
    assert "Simulation completed." in captured.out
    assert (output_dir / "zusammenfassung.json").exists()
