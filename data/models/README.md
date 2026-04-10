# Model data

The full BT-NextGen spectral grid is intentionally not committed to the GitHub repository because it is large and not suitable for a lightweight source checkout.

Expected local directory:

```text
data/models/bt-nextgen-agss2009/
```

The package resolves the full-spectrum model directory in this order:

1. `model_spec_dir=` passed to the Python API or CLI
2. `GENERAL_SED_MODEL_SPEC_DIR` environment variable
3. repository-local `data/models/bt-nextgen-agss2009/`

The bundled package still includes the lightweight BT-NextGen synthetic photometry files needed for offline photometric fitting.
