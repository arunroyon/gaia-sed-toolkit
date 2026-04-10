# Contributing

Thanks for contributing to `gaia-sed-toolkit`.

## Development workflow

1. Create a virtual environment.
2. Install the project in editable mode:

   ```bash
   pip install -e ".[dev]"
   ```

3. Run the local checks before opening a pull request:

   ```bash
   pytest
   ruff check .
   python -m build
   ```

## Repository conventions

- Put importable code in `src/general_sed`.
- Keep exploratory work in `notebooks/`.
- Treat `legacy/` as historical reference, not the active API.
- Keep generated figures and transient outputs under `outputs/`.
- Document any scientific assumptions, units, and catalog choices in docstrings or the README.

## Pull requests

- Prefer small, reviewable changes.
- Add or update tests for behavior changes.
- Avoid introducing hard-coded local filesystem paths.
- Preserve the scientific logic unless there is a documented reason to change it.

## Releases

See [`docs/release-checklist.md`](docs/release-checklist.md) before cutting a release.
