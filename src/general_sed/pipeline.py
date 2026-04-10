"""High-level end-to-end SED workflows."""

from __future__ import annotations

import tempfile
import zipfile
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from astroquery.gaia import Gaia

from .models import fit_model
from .photometry import (
    build_gaia_synthetic_table,
    build_observed_photometry_table,
    build_xp_sampled_spectrum,
    flux_wavel_dict,
)
from .plotting import plot_sed
from .resources import get_model_photometry_dir, get_model_spectra_dir


@dataclass(slots=True)
class SedResult:
    """Structured result returned by the SED pipeline."""

    xp_fits: Path
    observed_csv: Path
    synthetic_csv: Path
    plot_pdf: Path
    teff: int
    logg: float
    norm_band: str
    model_scale_factor: float
    model_resolution: float | None
    forced_teff: int | float | None
    forced_logg: float | None
    model_phot_file: Path
    model_spec_file: Path

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable dictionary representation."""

        result = asdict(self)
        for key, value in result.items():
            if isinstance(value, Path):
                result[key] = str(value)
        return result


def download_gaia_xp_continuous(
    source_id: int | str,
    out_dir: str | Path,
    overwrite: bool = False,
    verbose: bool = True,
) -> Path:
    """Download Gaia DR3 XP_CONTINUOUS data for a single source."""

    source_id = int(source_id)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    target_file = out_dir / f"XP_CONTINUOUS-Gaia DR3 {source_id}.fits"
    if target_file.exists() and not overwrite:
        if verbose:
            print(f"Using existing XP file: {target_file}")
        return target_file

    with tempfile.TemporaryDirectory() as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        old_cwd = Path.cwd()
        try:
            os.chdir(tmpdir)
            Gaia.load_data(
                ids=[source_id],
                data_release="Gaia DR3",
                retrieval_type="XP_CONTINUOUS",
                data_structure="INDIVIDUAL",
                format="fits",
                dump_to_file=True,
                overwrite_output_file=True,
                verbose=verbose,
            )

            zipfiles = sorted(tmpdir.glob("datalink_output_*.zip"))
            if not zipfiles:
                raise FileNotFoundError("Gaia.load_data did not create a datalink zip file.")

            extract_dir = tmpdir / "extracted"
            extract_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(zipfiles[-1], "r") as archive:
                archive.extractall(extract_dir)

            fits_candidates = list(extract_dir.rglob("*.fits"))
            if not fits_candidates:
                raise FileNotFoundError("No FITS file found inside Gaia datalink zip.")

            chosen = next((path for path in fits_candidates if str(source_id) in path.name), fits_candidates[0])
            shutil.move(str(chosen), str(target_file))
            if verbose:
                print(f"Downloaded XP_CONTINUOUS to: {target_file}")
            return target_file
        finally:
            os.chdir(old_cwd)


def fit_photometry(
    photometry: str | Path,
    model_phot_dir: str | Path | None = None,
    model_spec_dir: str | Path | None = None,
    norm_band: str | None = None,
    model_resolution: float | None = 60.0,
    force_model_teff: int | float | None = None,
    force_model_logg: float | None = None,
) -> dict[str, object]:
    """Fit BT-NextGen models to a local photometry CSV."""

    final_dic = flux_wavel_dict(photometry)
    fit = fit_model(
        final_dic=final_dic,
        model_phot_dir=model_phot_dir,
        model_spec_dir=model_spec_dir,
        norm_band=norm_band,
        model_resolution=model_resolution,
        force_teff=force_model_teff,
        force_logg=force_model_logg,
        include_spectrum=False,
    )
    return fit


def run_single_source_sed(
    source_id: int | str,
    a_v: float,
    xp_dir: str | Path,
    output_dir: str | Path,
    temp_dir: str | Path,
    model_phot_dir: str | Path | None = None,
    model_spec_dir: str | Path | None = None,
    overwrite_xp: bool = False,
    norm_band: str | None = None,
    model_resolution: float | None = 60.0,
    force_model_teff: int | float | None = None,
    force_model_logg: float | None = None,
) -> SedResult:
    """Run the full Gaia DR3 single-source SED workflow."""

    xp_dir = Path(xp_dir)
    output_dir = Path(output_dir)
    temp_dir = Path(temp_dir)
    gaia_name = f"Gaia DR3 {source_id}"

    resolved_model_phot_dir = get_model_photometry_dir(model_phot_dir)
    resolved_model_spec_dir = get_model_spectra_dir(model_spec_dir)

    xp_fits = download_gaia_xp_continuous(
        source_id=source_id,
        out_dir=xp_dir,
        overwrite=overwrite_xp,
        verbose=True,
    )

    temp_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    observed_csv = temp_dir / f"observed_{source_id}.csv"
    synthetic_csv = temp_dir / f"synthetic_{source_id}.csv"
    output_plot = output_dir / f"{source_id}_SED.pdf"

    observed_df = build_observed_photometry_table(source_id, a_v, observed_csv)
    synthetic_df = build_gaia_synthetic_table(xp_fits, a_v, synthetic_csv)
    xpsamp_df = build_xp_sampled_spectrum(xp_fits)
    final_dic = flux_wavel_dict(synthetic_df)

    fit = fit_model(
        final_dic=final_dic,
        model_phot_dir=resolved_model_phot_dir,
        model_spec_dir=resolved_model_spec_dir,
        norm_band=norm_band,
        model_resolution=model_resolution,
        force_teff=force_model_teff,
        force_logg=force_model_logg,
    )

    plot_sed(
        observed_phot=observed_df,
        synthetic_phot=synthetic_df,
        xpsamp=xpsamp_df,
        a_v=a_v,
        name=gaia_name,
        model_wave=fit["model_wave"],
        model_flux=fit["model_flux"],
        eff_temp=int(fit["teff"]),
        sur_g=float(fit["logg"]),
        savepath=output_plot,
        used_norm_band=str(fit["norm_band"]),
        model_resolution=model_resolution,
    )

    return SedResult(
        xp_fits=xp_fits,
        observed_csv=observed_csv,
        synthetic_csv=synthetic_csv,
        plot_pdf=output_plot,
        teff=int(fit["teff"]),
        logg=float(fit["logg"]),
        norm_band=str(fit["norm_band"]),
        model_scale_factor=float(fit["model_scale_factor"]),
        model_resolution=model_resolution,
        forced_teff=force_model_teff,
        forced_logg=force_model_logg,
        model_phot_file=Path(fit["model_phot_file"]),
        model_spec_file=Path(fit["model_spec_file"]),
    )
