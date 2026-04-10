"""Command-line interface for general_sed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import fit_photometry, run_single_source_sed
from .resources import get_model_photometry_dir, get_model_spectra_dir, get_repo_model_spectra_dir


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level CLI parser."""

    parser = argparse.ArgumentParser(prog="gaia-sed-toolkit", description="Gaia DR3 SED tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run-source", help="Run the full Gaia DR3 single-source SED workflow.")
    run.add_argument("source_id", type=int, help="Gaia DR3 source ID")
    run.add_argument("--av", type=float, default=0.0, help="Visual extinction A_V")
    run.add_argument("--xp-dir", type=Path, default=Path("data/examples/xp_continuous_fits"))
    run.add_argument("--output-dir", type=Path, default=Path("outputs/fig"))
    run.add_argument("--temp-dir", type=Path, default=Path("outputs/temp"))
    run.add_argument("--model-phot-dir", type=Path, default=None)
    run.add_argument("--model-spec-dir", type=Path, default=None)
    run.add_argument("--overwrite-xp", action="store_true")
    run.add_argument("--norm-band", type=str, default=None)
    run.add_argument("--model-resolution", type=float, default=60.0)
    run.add_argument("--force-model-teff", type=int, default=None)
    run.add_argument("--force-model-logg", type=float, default=None)

    fit = subparsers.add_parser("fit-photometry", help="Fit a local photometry CSV against BT-NextGen models.")
    fit.add_argument("photometry_csv", type=Path, help="Path to an observed or synthetic photometry CSV")
    fit.add_argument("--model-phot-dir", type=Path, default=None)
    fit.add_argument("--model-spec-dir", type=Path, default=None)
    fit.add_argument("--norm-band", type=str, default=None)
    fit.add_argument("--model-resolution", type=float, default=60.0)
    fit.add_argument("--force-model-teff", type=int, default=None)
    fit.add_argument("--force-model-logg", type=float, default=None)

    paths = subparsers.add_parser("show-paths", help="Show resolved data directories.")
    paths.add_argument("--json", action="store_true", help="Emit JSON instead of plain text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run-source":
        result = run_single_source_sed(
            source_id=args.source_id,
            a_v=args.av,
            xp_dir=args.xp_dir,
            output_dir=args.output_dir,
            temp_dir=args.temp_dir,
            model_phot_dir=args.model_phot_dir,
            model_spec_dir=args.model_spec_dir,
            overwrite_xp=args.overwrite_xp,
            norm_band=args.norm_band,
            model_resolution=args.model_resolution,
            force_model_teff=args.force_model_teff,
            force_model_logg=args.force_model_logg,
        )
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    if args.command == "fit-photometry":
        result = fit_photometry(
            photometry=args.photometry_csv,
            model_phot_dir=args.model_phot_dir,
            model_spec_dir=args.model_spec_dir,
            norm_band=args.norm_band,
            model_resolution=args.model_resolution,
            force_model_teff=args.force_model_teff,
            force_model_logg=args.force_model_logg,
        )
        serializable = {
            key: (str(value) if isinstance(value, Path) else value)
            for key, value in result.items()
            if key not in {"model_wave", "model_flux"}
        }
        print(json.dumps(serializable, indent=2))
        return 0

    phot_dir = get_model_photometry_dir()
    repo_spec_dir = get_repo_model_spectra_dir()
    try:
        spec_dir = get_model_spectra_dir()
    except Exception:
        spec_dir = None

    payload = {
        "model_photometry_dir": str(phot_dir),
        "model_spectra_dir": str(spec_dir) if spec_dir else None,
        "repo_model_spectra_dir": str(repo_spec_dir) if repo_spec_dir else None,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
