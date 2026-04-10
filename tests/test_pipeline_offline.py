from pathlib import Path

from general_sed import fit_photometry, get_model_photometry_dir


def test_offline_fit_with_example_data() -> None:
    photometry_csv = Path("data/examples/temp_sed_products/synthetic_5788625396770225152.csv")
    fit = fit_photometry(
        photometry=photometry_csv,
        model_phot_dir=get_model_photometry_dir(),
    )

    assert fit["teff"] > 0
    assert fit["logg"] > 0
    assert fit["norm_band"]
    assert Path(fit["model_phot_file"]).exists()
    assert fit["model_spec_file"] is None
