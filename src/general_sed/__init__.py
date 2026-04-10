"""General SED fitting and plotting tools for Gaia DR3 sources."""

from ._version import __version__
from .models import choose_norm_band, fit_model, parse_model_filename
from .photometry import (
    build_gaia_synthetic_table,
    build_observed_photometry_table,
    build_xp_sampled_spectrum,
    flux_wavel_dict,
)
from .pipeline import SedResult, fit_photometry, run_single_source_sed
from .plotting import plot_sed
from .resources import get_model_photometry_dir, get_model_spectra_dir

__all__ = [
    "__version__",
    "SedResult",
    "build_gaia_synthetic_table",
    "build_observed_photometry_table",
    "build_xp_sampled_spectrum",
    "choose_norm_band",
    "fit_model",
    "fit_photometry",
    "flux_wavel_dict",
    "get_model_photometry_dir",
    "get_model_spectra_dir",
    "parse_model_filename",
    "plot_sed",
    "run_single_source_sed",
]
