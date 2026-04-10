"""Photometry ingestion and flux-conversion utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier
from dust_extinction.parameter_averages import CCM89
from gaiaxpy import PhotometricSystem, calibrate, generate

from .constants import (
    AB_MAG_BANDS,
    BAND_WAVELENGTH_INFO,
    GAIAXPY_TO_INTERNAL,
    VEGA_MAG_BANDS,
)


def get_dataframe(df_or_file: pd.DataFrame | str | Path) -> pd.DataFrame:
    """Return a dataframe from an in-memory table or CSV path."""

    if isinstance(df_or_file, pd.DataFrame):
        return df_or_file.copy()
    return pd.read_csv(df_or_file)


def build_observed_photometry_table(
    source_id: int | str,
    av: float,
    out_csv: str | Path | None = None,
) -> pd.DataFrame:
    """Query observed photometry from Gaia, 2MASS, and AllWISE."""

    source_id = str(source_id)
    gaia_name = f"Gaia DR3 {source_id}"

    vizier = Vizier(columns=["*", "+_r"])
    vizier.ROW_LIMIT = 5

    row: dict[str, Any] = {"Name": gaia_name, "Av": av, "Dist": np.nan}

    gaia = vizier.query_constraints(catalog="I/355/gaiadr3", Source=source_id)
    if len(gaia) == 0 or len(gaia[0]) == 0:
        gaia = vizier.query_constraints(catalog="I/350/gaiaedr3", Source=source_id)
    if len(gaia) == 0 or len(gaia[0]) == 0:
        raise ValueError(f"Gaia source {source_id} not found in Vizier.")

    source_row = gaia[0][0]
    ra = float(source_row["RA_ICRS"])
    dec = float(source_row["DE_ICRS"])

    row["RA"] = ra
    row["DEC"] = dec
    for band in ("Gmag", "BPmag", "RPmag"):
        row[band] = float(source_row[band]) if band in source_row.colnames else np.nan
        row[f"e_{band}"] = (
            float(source_row[f"e_{band}"])
            if f"e_{band}" in source_row.colnames
            else np.nan
        )

    try:
        dist = vizier.query_constraints(catalog="I/352/gedr3dis", Source=source_id)
        if len(dist) > 0 and len(dist[0]) > 0 and "rgeo" in dist[0].colnames:
            row["Dist"] = float(dist[0][0]["rgeo"])
    except Exception:
        pass

    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg)
    _populate_2mass(vizier, coord, row)
    _populate_wise(vizier, coord, row)

    frame = pd.DataFrame([row])
    if out_csv is not None:
        out_path = Path(out_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(out_path, index=False)
    return frame


def _populate_2mass(vizier: Vizier, coord: SkyCoord, row: dict[str, Any]) -> None:
    try:
        twomass = vizier.query_region(coord, radius=5 * u.arcsec, catalog="II/246/out")
        if len(twomass) == 0 or len(twomass[0]) == 0:
            return
        source = twomass[0][0]
        row["Jmag"] = float(source["Jmag"]) if "Jmag" in source.colnames else np.nan
        row["e_Jmag"] = float(source["e_Jmag"]) if "e_Jmag" in source.colnames else np.nan
        row["Hmag"] = float(source["Hmag"]) if "Hmag" in source.colnames else np.nan
        row["e_Hmag"] = float(source["e_Hmag"]) if "e_Hmag" in source.colnames else np.nan
        row["Ksmag"] = float(source["Kmag"]) if "Kmag" in source.colnames else np.nan
        row["e_Ksmag"] = float(source["e_Kmag"]) if "e_Kmag" in source.colnames else np.nan
    except Exception:
        return


def _populate_wise(vizier: Vizier, coord: SkyCoord, row: dict[str, Any]) -> None:
    try:
        wise = vizier.query_region(coord, radius=5 * u.arcsec, catalog="II/328/allwise")
        if len(wise) == 0 or len(wise[0]) == 0:
            return
        source = wise[0][0]
        for band in ("W1mag", "W2mag", "W3mag", "W4mag"):
            row[band] = float(source[band]) if band in source.colnames else np.nan
            row[f"e_{band}"] = (
                float(source[f"e_{band}"])
                if f"e_{band}" in source.colnames
                else np.nan
            )
    except Exception:
        return


def build_gaia_synthetic_table(
    xp_fits: str | Path,
    av: float,
    out_csv: str | Path | None = None,
) -> pd.DataFrame:
    """Generate synthetic photometry from a Gaia XP_CONTINUOUS FITS file."""

    phot_systems = [
        PhotometricSystem.JKC,
        PhotometricSystem.SDSS,
        PhotometricSystem.IPHAS,
        PhotometricSystem.Gaia_DR3_Vega,
    ]
    synthetic = generate(str(xp_fits), photometric_system=phot_systems)
    source_id = str(synthetic["source_id"].iloc[0])

    row: dict[str, Any] = {"Name": f"Gaia DR3 {source_id}", "Av": av, "Dist": 0.0}
    for column in synthetic.columns:
        if column in GAIAXPY_TO_INTERNAL:
            internal_name = GAIAXPY_TO_INTERNAL[column]
            row[internal_name] = float(synthetic[column].iloc[0])
            row[f"e_{internal_name}"] = 0.1

    frame = pd.DataFrame([row])
    if out_csv is not None:
        out_path = Path(out_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(out_path, index=False)
    return frame


def build_xp_sampled_spectrum(xp_fits: str | Path) -> pd.DataFrame:
    """Calibrate a Gaia XP spectrum onto a geometric wavelength grid."""

    spectra, sampling = calibrate(str(xp_fits), sampling=np.geomspace(336, 1020, 342))
    return pd.DataFrame(
        {
            "wavelength": list(sampling),
            "flux": list(spectra["flux"][0]),
            "flux_error": list(spectra["flux_error"][0]),
        }
    )


def flux_wavel_dict(phot_input: pd.DataFrame | str | Path) -> dict[str, list[float]]:
    """Convert magnitudes into dereddened ``lambda * F_lambda`` values."""

    star_phot_data = get_dataframe(phot_input)
    row = star_phot_data.iloc[0]
    av = float(row.get("Av", 0.0))

    final: dict[str, list[float]] = {}
    for band, bandinfo in BAND_WAVELENGTH_INFO.items():
        if band not in row.index or pd.isna(row[band]):
            continue

        _, wavelength_a, zero_mag_flux_jy, a_lambda_over_av = bandinfo
        mag = float(row[band])
        mag_dered = mag - a_lambda_over_av * av

        err_col = f"e_{band}"
        mag_err = (
            float(row[err_col])
            if err_col in row.index and pd.notna(row[err_col])
            else 0.1
        )
        if mag_err > 90:
            mag_err = 0.0

        if band in VEGA_MAG_BANDS:
            flux_val = _mag_to_flux_lambda_f_lambda(mag_dered, zero_mag_flux_jy, wavelength_a)
            flux_err_val = _mag_to_flux_lambda_f_lambda(
                mag_dered + mag_err,
                zero_mag_flux_jy,
                wavelength_a,
            )
        elif band in AB_MAG_BANDS:
            flux_val = _mag_to_flux_lambda_f_lambda(mag_dered, 3631.0, wavelength_a)
            flux_err_val = _mag_to_flux_lambda_f_lambda(
                mag_dered + mag_err,
                3631.0,
                wavelength_a,
            )
        else:
            continue

        final[band] = [
            float(wavelength_a),
            float(flux_val),
            float(abs(flux_val - flux_err_val)),
        ]

    if not final:
        raise ValueError("No usable photometric bands found.")

    return dict(sorted(final.items(), key=lambda item: item[1][0]))


def deredden_xp_spectrum(xp_sampled: pd.DataFrame | str | Path, a_v: float) -> pd.DataFrame:
    """Return a dereddened Gaia XP sampled spectrum."""

    xp_df = get_dataframe(xp_sampled)
    xp_wave_a = xp_df["wavelength"].to_numpy(dtype=float) * 10.0
    xp_flux = xp_df["flux"].to_numpy(dtype=float) / 10.0

    ext_model = CCM89(Rv=3.1)
    transmission = ext_model.extinguish(xp_wave_a * u.AA, Av=a_v)
    xp_flux_dered = xp_flux / transmission * 1000.0
    return pd.DataFrame({"wavelength": xp_wave_a, "flux": xp_flux_dered})


def _mag_to_flux_lambda_f_lambda(
    magnitude: float,
    zero_point_jy: float,
    wavelength_a: float,
) -> float:
    return (2.99792458e-05 * (zero_point_jy * 10 ** (-magnitude / 2.5))) / (wavelength_a**2)
