# FS26 Python Bank

Function-based Python implementation for the FS26 Python Bank assignment.

Implementation code and tests use English names.
Moodle-facing JSON keys and existing assignment documentation may stay German where that matches the official wording.

## Contents

- `docs/assignment-summary.md` summarizes the Moodle assignment.
- `docs/system-overview.md` describes the intended system architecture.
- `docs/components/` contains component notes for the future implementation.
- `docs/transaction-format.md` documents the expected transaction data shape.
- `src/python_bank/` contains the implementation.
- `tests/` contains unit tests and the optional Moodle reference comparison.
- `pyproject.toml` and `uv.lock` keep the Python project environment reproducible.

## Setup

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest
```

If the local Moodle reference data is available, the test suite also compares generated output against the official reference files.

## Expected Implementation Shape

The Moodle assignment expects a function-based Python implementation with these responsibilities:

- transaction engine
- account management
- credit management
- internal bank bookkeeping
- JSON input and output

No classes, UI, generated output, or reference test data are committed to this repository.

## Moodle Reference Data

The official Moodle archive is course-private and should stay local.
Download the "Transaktionsdaten Python Bank" resource into `.local/moodle-reference/` and extract it there.
The file is named as a PDF in Moodle, but it is a ZIP archive.

Expected local structure:

```text
.local/moodle-reference/extracted/
  transaktionen/
  konten/
  bankkonten.json
  zusammenfassung.json
```

Run the full reference simulation manually:

```bash
uv run python-bank --transaction-file .local/moodle-reference/extracted/transaktionen --output-dir .tmp-output/reference-run
```
