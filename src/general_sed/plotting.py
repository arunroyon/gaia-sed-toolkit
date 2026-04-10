"""Plotting utilities for SED products."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .photometry import deredden_xp_spectrum, flux_wavel_dict

mpl.rcParams["text.usetex"] = False


def setup_plot_style() -> None:
    """Apply a consistent plotting style."""

    plt.rcParams["text.usetex"] = False
    plt.rcParams["figure.figsize"] = (15, 10)
    plt.rcParams["axes.linewidth"] = 2
    plt.rcParams["xtick.major.size"] = 25
    plt.rcParams["xtick.minor.size"] = 5
    plt.rcParams["ytick.major.size"] = 25
    plt.rcParams["ytick.minor.size"] = 5
    plt.rcParams["xtick.major.width"] = 2
    plt.rcParams["ytick.major.width"] = 2
    plt.rcParams["xtick.minor.width"] = 1
    plt.rcParams["ytick.minor.width"] = 1
    plt.rcParams["xtick.minor.visible"] = True
    plt.rcParams["ytick.minor.visible"] = True
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.top"] = True
    plt.rcParams["ytick.right"] = True


def plot_sed(
    observed_phot: pd.DataFrame | str | Path,
    synthetic_phot: pd.DataFrame | str | Path,
    xpsamp: pd.DataFrame | str | Path,
    a_v: float,
    name: str,
    model_wave: np.ndarray,
    model_flux: np.ndarray,
    eff_temp: int,
    sur_g: float,
    savepath: str | Path,
    used_norm_band: str | None = None,
    model_resolution: float | None = None,
) -> Path:
    """Create and save an SED summary figure."""

    setup_plot_style()
    obs_dict = flux_wavel_dict(observed_phot)
    syn_dict = flux_wavel_dict(synthetic_phot)

    fig = plt.figure(facecolor="white")

    x_obs = [obs_dict[k][0] for k in obs_dict]
    y_obs = [obs_dict[k][1] for k in obs_dict]
    z_obs = [obs_dict[k][2] for k in obs_dict]
    plt.errorbar(
        x_obs,
        y_obs,
        yerr=z_obs,
        marker="v",
        ms=13,
        mfc="red",
        mec="red",
        ls="none",
        label="Observed photometric flux",
    )

    x_syn = [syn_dict[k][0] for k in syn_dict]
    y_syn = [syn_dict[k][1] for k in syn_dict]
    z_syn = [syn_dict[k][2] for k in syn_dict]
    plt.errorbar(
        x_syn,
        y_syn,
        yerr=z_syn,
        marker="o",
        ms=12,
        mfc="none",
        mec="k",
        mew=2.0,
        ls="none",
        label="Gaia synthetic photometric flux",
    )

    model_label = f"BT-NextGen\nTeff = {eff_temp} K, log g = {sur_g}"
    if model_resolution is not None:
        model_label = (
            "BT-NextGen smoothed\n"
            f"Teff = {eff_temp} K, log g = {sur_g}, R = {model_resolution:.0f}"
        )

    good_model = np.isfinite(model_wave) & np.isfinite(model_flux) & (model_flux > 0)
    plt.plot(
        np.asarray(model_wave)[good_model],
        np.asarray(model_flux)[good_model],
        "k-",
        linewidth=1.5,
        alpha=0.7,
        label=model_label,
    )

    xp_dered = deredden_xp_spectrum(xpsamp, a_v)
    plt.plot(
        xp_dered["wavelength"].to_numpy(dtype=float),
        xp_dered["flux"].to_numpy(dtype=float),
        linewidth=2.2,
        color="g",
        label="Gaia XP spectrum",
    )

    plt.tick_params(
        direction="in",
        which="major",
        labelsize=15,
        length=8,
        width=2,
        colors="k",
        bottom=True,
        top=True,
        left=True,
        right=True,
    )
    plt.xticks(weight="bold")
    plt.yticks(weight="bold")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Wavelength ($\\AA$)", fontsize=18, fontweight="bold")
    plt.ylabel("$\\lambda F_\\lambda$ $(erg/cm^2/s)$", fontsize=18, fontweight="bold")

    x_all = np.array(x_obs + x_syn + list(xp_dered["wavelength"]), dtype=float)
    y_all = np.array(y_obs + y_syn + list(xp_dered["flux"]), dtype=float)
    y_pos = y_all[np.isfinite(y_all) & (y_all > 0)]
    plt.xlim(np.nanmin(x_all) * 0.9, np.nanmax(x_all) * 1.05)
    plt.ylim(np.nanmin(y_pos) * 0.5, np.nanmax(y_pos) * 2.0)

    title = name if used_norm_band is None else f"{name}"
    plt.title(title, fontsize=18, fontweight="bold")
    plt.legend(prop={"size": 14, "weight": "bold"}, ncol=1)

    fig.set_size_inches(13.5, 7.5)
    try:
        plt.tight_layout()
    except Exception:
        pass

    savepath = Path(savepath)
    savepath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(savepath, bbox_inches="tight", dpi=300)
    plt.close(fig)
    return savepath
