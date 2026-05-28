# Development

This repository is currently a scaffold.
It contains documentation and uv project metadata, but no implementation code or test data.

## Environment

Run:

```bash
uv sync
```

This verifies that the Python project metadata is valid and creates the local environment.

## Future Implementation

When implementation work starts, add the assignment modules deliberately and keep them function-based:

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

## Verification

There is no test suite in this scaffold yet.
When code is added, include representative tests and update this page with the exact commands.
