# Development

Code, tests, CLI output, and developer-facing project structure use English names.
Existing German documentation may stay German where it mirrors the Moodle assignment.

## Environment

Run:

```bash
uv sync
```

This verifies that the Python project metadata is valid and creates the local environment.

Run the tests:

```bash
uv run pytest
```

## Future Implementation

The implementation is function-based and lives under `src/python_bank/`:

- transaction engine
- account management
- credit management
- internal bank bookkeeping
- JSON input and output

Keep generated files out of Git:

- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `*.egg-info/`
- `output/`
- `.tmp-output/`
- `.local/`

## Verification

The test suite includes unit tests and an exact comparison against committed reference data under `data/reference/`.
Generated output and logs must stay in ignored `output/`, `.tmp-output/`, or `logs/`.
