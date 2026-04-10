# general-sed

`general-sed` packages the existing Gaia DR3 single-source SED workflow in this repository into a reusable Python library and CLI. It preserves the current scientific flow: Gaia XP download, observed photometry lookup, Gaia synthetic photometry generation, BT-NextGen model selection, scaling, and publication-style plotting.

The repository is organized for both research use and open-source distribution. Library code lives in `src/general_sed`, legacy material is retained in `legacy/`, example assets are separated from generated outputs, and the package is installable with standard Python packaging tools.

## Features

- Installable with `pip install .` and `pip install git+<repo_url>`
- Clean import API for Python users
- CLI for local photometry fitting and full Gaia DR3 single-source runs
- Bundled BT-NextGen synthetic photometry grid for installable offline model matching
- Repository-local discovery of the larger BT-NextGen spectral grid
- Offline smoke tests for import, model parsing, and photometry-to-model fitting

## Installation

### From a local checkout

```bash
pip install .
```

### From GitHub

```bash
pip install "git+<repo_url>"
```

### Development install

```bash
pip install -e ".[dev]"
```

## Data requirements

The package bundles the lightweight BT-NextGen synthetic photometry grid used for model matching.

The full BT-NextGen spectral grid is much larger and is intentionally kept as external repository data rather than bundled into the wheel. The package looks for full spectra in this order:

1. `model_spec_dir=` passed to the API or CLI
2. `GENERAL_SED_MODEL_SPEC_DIR` environment variable
3. Repository-local `data/models/bt-nextgen-agss2009/`

This means:

- `pip install .` inside this repository works with the local model directory already present here
- `pip install git+...` or a future PyPI install can still do photometric model matching out of the box
- the full Gaia XP plus BT-NextGen spectrum plotting workflow still needs the external spectral grid

## Quickstart

### Python API

```python
from pathlib import Path

from general_sed import run_single_source_sed

result = run_single_source_sed(
    source_id=5788625396770225152,
    a_v=0.0,
    xp_dir=Path("data/examples/xp_continuous_fits"),
    output_dir=Path("outputs/fig"),
    temp_dir=Path("outputs/temp"),
)

print(result.to_dict())
```

### Local photometry fitting

```python
from general_sed import fit_photometry

fit = fit_photometry("data/examples/temp_sed_products/synthetic_5788625396770225152.csv")
print(fit["teff"], fit["logg"])
```

### CLI usage

Inspect available data paths:

```bash
general-sed show-paths
```

Fit a local photometry file:

```bash
general-sed fit-photometry data/examples/temp_sed_products/synthetic_5788625396770225152.csv
```

Run the full single-source pipeline:

```bash
general-sed run-source 5788625396770225152 --av 0.0
```

## Inputs and outputs

### Inputs

- Gaia DR3 source ID for the online single-source pipeline
- Optional extinction value `A_V`
- BT-NextGen model directories when running outside a repository checkout
- Local photometry CSV for offline fitting workflows

### Outputs

- Observed photometry CSV
- Gaia synthetic photometry CSV
- SED plot PDF
- Fit metadata including `Teff`, `log g`, normalization band, and scale factor

## Package structure

```text
src/general_sed/          Installable package
tests/                    Offline smoke and functional tests
examples/                 Example scripts
data/examples/            Example FITS and CSV assets
data/models/              External BT-NextGen spectral grid
notebooks/                Original and exploratory notebooks
legacy/                   Legacy pre-package script
outputs/                  Generated figures and transient products
```

## Scientific notes

- Wavelengths are handled in Angstrom.
- Flux conversion uses `lambda * F_lambda` in cgs-style units following the original project logic.
- Extinction handling uses `dust_extinction.parameter_averages.CCM89`.
- Model smoothing approximates constant resolving power in log-wavelength space.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
python -m build
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contributor workflow and [`docs/release-checklist.md`](docs/release-checklist.md) for release preparation.

## Citation and attribution

If this repository contributes to published work, cite the software repository and the astronomical data products it depends on, including Gaia DR3, GaiaXPy, Astroquery, Astropy, and the BT-NextGen model grid.

## License

This repository currently uses the MIT License as a practical open-source default. If the original project owner intends a different license, update [`LICENSE`](LICENSE) before the first public release.
