from pathlib import Path

import pytest

from python_bank.engine import run_bank_simulation
REFERENCE_ROOT = Path(".local/moodle-reference/extracted")


def require_reference_data() -> Path:
    if not (REFERENCE_ROOT / "transaktionen").exists():
        pytest.skip("Moodle reference data is not available locally.")
    return REFERENCE_ROOT


def test_full_moodle_reference_output_matches(tmp_path):
    reference = require_reference_data()
    output_dir = tmp_path / "reference-run"

    run_bank_simulation(reference / "transaktionen", output_dir)

    assert (output_dir / "zusammenfassung.json").read_bytes() == (reference / "zusammenfassung.json").read_bytes()
    assert (output_dir / "bankkonten.json").read_bytes() == (reference / "bankkonten.json").read_bytes()

    expected_accounts = sorted((reference / "konten").glob("*.json"))
    assert expected_accounts
    for expected_file in expected_accounts:
        actual_file = output_dir / "konten" / expected_file.name
        assert actual_file.exists(), expected_file.name
        assert actual_file.read_bytes() == expected_file.read_bytes(), expected_file.name
