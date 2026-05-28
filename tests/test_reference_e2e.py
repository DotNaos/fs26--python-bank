from pathlib import Path

from python_bank.engine import run_bank_simulation


REFERENCE_ROOT = Path("data/reference")


def test_full_moodle_reference_output_matches(tmp_path):
    output_dir = tmp_path / "reference-run"

    run_bank_simulation(REFERENCE_ROOT / "transaktionen", output_dir)

    assert (output_dir / "zusammenfassung.json").read_bytes() == (REFERENCE_ROOT / "zusammenfassung.json").read_bytes()
    assert (output_dir / "bankkonten.json").read_bytes() == (REFERENCE_ROOT / "bankkonten.json").read_bytes()

    expected_accounts = sorted((REFERENCE_ROOT / "konten").glob("*.json"))
    assert expected_accounts
    for expected_file in expected_accounts:
        actual_file = output_dir / "konten" / expected_file.name
        assert actual_file.exists(), expected_file.name
        assert actual_file.read_bytes() == expected_file.read_bytes(), expected_file.name
