"""Minimal offline example using the bundled fitting workflow."""

from __future__ import annotations

from pathlib import Path

from general_sed import fit_photometry


def main() -> None:
    photometry_csv = Path("data/examples/temp_sed_products/synthetic_5788625396770225152.csv")
    fit = fit_photometry(photometry_csv)
    print(f"Best-fit Teff: {fit['teff']} K")
    print(f"Best-fit log g: {fit['logg']}")
    print(f"Normalization band: {fit['norm_band']}")


if __name__ == "__main__":
    main()
