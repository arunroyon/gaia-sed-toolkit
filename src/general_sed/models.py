"""BT-NextGen model selection and scaling helpers."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from astropy.io import ascii
from scipy.ndimage import gaussian_filter1d

from .constants import DEFAULT_NORM_BAND_PREFERENCE
from .resources import get_model_photometry_dir, get_model_spectra_dir


def near(array: np.ndarray, value: float) -> int:
    """Return the index of the nearest value in an array."""

    array = np.asarray(array, dtype=float)
    return int(np.abs(array - value).argmin())


def choose_norm_band(final_dic: dict[str, list[float]], norm_band: str | None = None) -> str:
    """Choose or validate the band used to normalize the model."""

    if norm_band is not None:
        if norm_band not in final_dic:
            raise ValueError(
                f"Requested normalization band '{norm_band}' is not available. "
                f"Available bands: {list(final_dic.keys())}"
            )
        return norm_band

    for band in DEFAULT_NORM_BAND_PREFERENCE:
        if band in final_dic:
            return band
    return next(iter(final_dic))


def smooth_spectrum_to_resolution(
    wave: np.ndarray,
    flux: np.ndarray,
    resolving_power: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Approximate Gaussian smoothing at constant resolving power in log-lambda space."""

    wave = np.asarray(wave, dtype=float)
    flux = np.asarray(flux, dtype=float)

    good = np.isfinite(wave) & np.isfinite(flux) & (wave > 0)
    wave = wave[good]
    flux = flux[good]

    if resolving_power is None or resolving_power <= 0:
        return wave, flux

    idx = np.argsort(wave)
    wave = wave[idx]
    flux = flux[idx]

    logw = np.log(wave)
    logw_uniform = np.linspace(logw.min(), logw.max(), len(logw))
    flux_uniform = np.interp(logw_uniform, logw, flux)

    dlog = np.median(np.diff(logw_uniform))
    sigma_log = (1.0 / resolving_power) / 2.354820045
    sigma_pix = sigma_log / dlog
    if sigma_pix < 0.3:
        return np.exp(logw_uniform), flux_uniform

    flux_smooth = gaussian_filter1d(flux_uniform, sigma_pix, mode="nearest")
    return np.exp(logw_uniform), flux_smooth


def parse_model_filename(filename: str) -> tuple[int, float]:
    """Parse BT-NextGen model filenames into ``(teff, logg)``."""

    match = re.search(r"lte(\d{3})-([0-9]\.[0-9])", filename)
    if match is None:
        raise ValueError(f"Could not parse model filename: {filename}")
    return int(match.group(1)) * 100, float(match.group(2))


def find_model_phot_file(model_phot_dir: str | Path, teff: int | float, logg: float) -> Path:
    """Locate a photometric BT-NextGen file for a given model."""

    model_phot_dir = Path(model_phot_dir)
    teff = int(round(float(teff)))
    logg = float(logg)

    candidates = _matching_model_files(model_phot_dir, teff, logg)
    if not candidates:
        raise FileNotFoundError(f"No model photometry file found for Teff={teff}, log g={logg}")
    return candidates[0]


def find_model_spec_file(model_spec_dir: str | Path, teff: int | float, logg: float) -> Path:
    """Locate a full-spectrum BT-NextGen file for a given model."""

    model_spec_dir = Path(model_spec_dir)
    teff = int(round(float(teff)))
    logg = float(logg)

    candidates = _matching_model_files(model_spec_dir, teff, logg)
    if not candidates:
        raise FileNotFoundError(f"No model spectrum file found for Teff={teff}, log g={logg}")
    return candidates[0]


def _matching_model_files(model_dir: Path, teff: int, logg: float) -> list[Path]:
    candidates: list[Path] = []
    for filename in model_dir.iterdir():
        try:
            parsed_teff, parsed_logg = parse_model_filename(filename.name)
        except Exception:
            continue
        if parsed_teff == teff and abs(parsed_logg - logg) < 1e-6:
            candidates.append(filename)
    return sorted(candidates, key=lambda item: ("a+0.0" not in item.name, item.name))


def fit_model(
    final_dic: dict[str, list[float]],
    model_phot_dir: str | Path | None = None,
    model_spec_dir: str | Path | None = None,
    norm_band: str | None = None,
    model_resolution: float | None = 60.0,
    force_teff: int | float | None = None,
    force_logg: float | None = None,
    include_spectrum: bool = True,
) -> dict[str, object]:
    """Fit or force-select a BT-NextGen model against photometric fluxes."""

    phot_dir = get_model_photometry_dir(model_phot_dir)
    spectra_dir = get_model_spectra_dir(model_spec_dir) if include_spectrum else None

    sed_fitting_bands = list(final_dic.keys())
    used_norm_band = choose_norm_band(final_dic, norm_band=norm_band)
    norm_wave = final_dic[used_norm_band][0]
    norm_flux = final_dic[used_norm_band][1]

    if force_teff is not None and force_logg is not None:
        eff_temp = int(round(float(force_teff)))
        sur_g = float(force_logg)
        best_phot_file = find_model_phot_file(phot_dir, eff_temp, sur_g)
        best_spec_file = find_model_spec_file(spectra_dir, eff_temp, sur_g) if spectra_dir else None
    else:
        least_sq_theo_sed: dict[Path, float] = {}
        phot_file_map: dict[Path, tuple[int, float]] = {}

        for filepath in phot_dir.iterdir():
            try:
                data = ascii.read(filepath)
                a_wave = np.array(data.columns[1], dtype=float)
                b_flux = np.array(data.columns[2], dtype=float)
                teff_trial, logg_trial = parse_model_filename(filepath.name)
            except Exception:
                continue

            idx_norm = near(a_wave, norm_wave)
            if b_flux[idx_norm] == 0:
                continue

            scale_factor_trial = norm_flux / b_flux[idx_norm]
            norm_phot_flux = b_flux * scale_factor_trial
            chi2 = []
            for band in sed_fitting_bands:
                idx = near(a_wave, final_dic[band][0])
                model_flux = norm_phot_flux[idx]
                obs_flux = final_dic[band][1]
                obs_err = max(final_dic[band][2], 1e-30)
                chi2.append(((obs_flux - model_flux) / obs_err) ** 2)

            least_sq_theo_sed[filepath] = float(np.sum(chi2))
            phot_file_map[filepath] = (teff_trial, logg_trial)

        if not least_sq_theo_sed:
            raise ValueError("No valid model photometry files were read.")

        best_phot_file = min(least_sq_theo_sed, key=least_sq_theo_sed.get)
        eff_temp, sur_g = phot_file_map[best_phot_file]
        best_spec_file = find_model_spec_file(spectra_dir, eff_temp, sur_g) if spectra_dir else None

    data_phot = ascii.read(best_phot_file)
    a_wave = np.array(data_phot.columns[1], dtype=float)
    b_flux = np.array(data_phot.columns[2], dtype=float)

    idx_norm = near(a_wave, norm_wave)
    if b_flux[idx_norm] == 0:
        raise ValueError("Selected model has zero flux in the normalization band.")

    scale_factor = norm_flux / b_flux[idx_norm]

    model_wave = None
    model_flux = None
    if best_spec_file is not None:
        data_spec = ascii.read(best_spec_file)
        spec_wave = np.array(data_spec.columns[0], dtype=float)
        spec_flux = np.array(data_spec.columns[1], dtype=float) * scale_factor
        model_wave, model_flux = smooth_spectrum_to_resolution(
            spec_wave,
            spec_flux,
            resolving_power=model_resolution,
        )

    return {
        "model_wave": model_wave,
        "model_flux": model_flux,
        "teff": int(eff_temp),
        "logg": float(sur_g),
        "norm_band": used_norm_band,
        "model_scale_factor": float(scale_factor),
        "model_phot_file": best_phot_file,
        "model_spec_file": best_spec_file,
        "model_resolution": model_resolution,
    }
