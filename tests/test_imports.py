from general_sed import __version__, fit_photometry, parse_model_filename


def test_imports_expose_public_api() -> None:
    assert __version__ == "0.1.0"
    assert callable(fit_photometry)
    assert callable(parse_model_filename)
