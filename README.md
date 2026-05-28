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
- `tests/` contains unit tests and the Moodle reference comparison.
- `data/reference/` contains the bundled seed and reference data.
- `pyproject.toml` and `uv.lock` keep the Python project environment reproducible.

## Setup

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest
```

The test suite compares generated output against the bundled reference files.

## Expected Implementation Shape

The Moodle assignment expects a function-based Python implementation with these responsibilities:

- transaction engine
- account management
- credit management
- internal bank bookkeeping
- JSON input and output

No classes, UI, generated output, or logs are committed to this repository.

## Moodle Reference Data

The seed and reference data is committed under:

```text
data/reference/
  transaktionen/
  konten/
  bankkonten.json
  zusammenfassung.json
```

Run the simulator with explicit paths:

```bash
uv run python-bank --transaction-file data/reference/transaktionen --output-dir output/reference-run
```

Run `uv run python-bank` without arguments to open the small interactive terminal menu.
