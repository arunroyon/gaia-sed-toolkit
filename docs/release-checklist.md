# Release checklist

## Before tagging

1. Update the version in `src/general_sed/_version.py` and `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Run:

   ```bash
   pytest
   ruff check .
   python -m build
   ```

4. Confirm the README installation examples still work.
5. Confirm the intended license text is correct.
6. Confirm how the large BT-NextGen spectral grid will be distributed for users outside the repository checkout.

## Build artifacts

```bash
python -m build
```

This creates:

- `dist/*.tar.gz` source distribution
- `dist/*.whl` wheel distribution

## Publish to PyPI

```bash
twine check dist/*
twine upload dist/*
```

## After release

1. Create a GitHub release.
2. Attach or link any external model-grid distribution assets if needed.
3. Announce the release with install instructions and model-data guidance.
