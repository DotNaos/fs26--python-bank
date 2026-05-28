# FS26 Python Bank

Scaffold repository for the FS26 Python Bank assignment.

This repository intentionally contains only the project documentation and uv setup.
Implementation code, tests, reference test data, generated output, and local cache files are not included.

## Contents

- `docs/assignment-summary.md` summarizes the Moodle assignment.
- `docs/system-overview.md` describes the intended system architecture.
- `docs/components/` contains component notes for the future implementation.
- `docs/transaction-format.md` documents the expected transaction data shape.
- `pyproject.toml` and `uv.lock` keep the Python project environment reproducible.

## Setup

```bash
uv sync
```

The current scaffold has no runtime package and no test suite yet.
Future implementation work should add the required Python modules and tests back deliberately.

## Expected Implementation Shape

The Moodle assignment expects a function-based Python implementation with these responsibilities:

- transaction engine
- account management
- credit management
- internal bank bookkeeping
- JSON input and output

No classes, UI, generated output, or reference test data are part of this scaffold.
