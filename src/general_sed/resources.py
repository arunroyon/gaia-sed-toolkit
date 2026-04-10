"""Helpers for locating packaged and external data resources."""

from __future__ import annotations

import os
from importlib.resources import as_file, files
from pathlib import Path

from .exceptions import MissingModelDataError


def _package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_existing(candidate: Path | None) -> Path | None:
    if candidate is None:
        return None
    if candidate.exists():
        return candidate.resolve()
    return None


def get_repo_model_spectra_dir() -> Path | None:
    """Return the repository-local BT-NextGen spectra directory when present."""

    candidates = [
        _repo_root() / "data" / "models" / "bt-nextgen-agss2009",
        _repo_root() / "bt-nextgen-agss2009",
    ]
    for candidate in candidates:
        resolved = _resolve_existing(candidate)
        if resolved is not None:
            return resolved
    return None


def get_model_spectra_dir(path: str | os.PathLike[str] | None = None) -> Path:
    """Resolve the BT-NextGen full-spectrum directory.

    Resolution order:
    1. Explicit function argument.
    2. ``GENERAL_SED_MODEL_SPEC_DIR`` environment variable.
    3. Repository-local data directory, when available.
    """

    explicit = _resolve_existing(Path(path).expanduser() if path else None)
    if explicit is not None:
        return explicit

    env_path = os.environ.get("GENERAL_SED_MODEL_SPEC_DIR")
    env_resolved = _resolve_existing(Path(env_path).expanduser() if env_path else None)
    if env_resolved is not None:
        return env_resolved

    repo_path = get_repo_model_spectra_dir()
    if repo_path is not None:
        return repo_path

    raise MissingModelDataError(
        "BT-NextGen full-spectrum files were not found. "
        "Set GENERAL_SED_MODEL_SPEC_DIR or pass model_spec_dir=..."
    )


def get_model_photometry_dir(path: str | os.PathLike[str] | None = None) -> Path:
    """Resolve the BT-NextGen synthetic photometry directory."""

    explicit = _resolve_existing(Path(path).expanduser() if path else None)
    if explicit is not None:
        return explicit

    env_path = os.environ.get("GENERAL_SED_MODEL_PHOT_DIR")
    env_resolved = _resolve_existing(Path(env_path).expanduser() if env_path else None)
    if env_resolved is not None:
        return env_resolved

    return get_packaged_model_photometry_dir()


def get_packaged_model_photometry_dir() -> Path:
    """Return the bundled BT-NextGen synthetic photometry directory."""

    resource = (
        files("general_sed")
        / "data"
        / "model_photometry"
        / "bt-nextgen-agss2009_phot_1587193332.0893"
    )
    with as_file(resource) as resource_path:
        return Path(resource_path)


def get_example_data_dir() -> Path:
    """Return the repository example-data directory when present."""

    candidates = [
        _repo_root() / "data" / "examples",
        _package_root() / "general_sed" / "data" / "examples",
    ]
    for candidate in candidates:
        resolved = _resolve_existing(candidate)
        if resolved is not None:
            return resolved
    raise FileNotFoundError("Example data directory could not be located.")
