from general_sed import choose_norm_band, parse_model_filename


def test_parse_model_filename() -> None:
    teff, logg = parse_model_filename("lte027-4.5-0.0a+0.0.BT-NextGen.7.dat.txt")
    assert teff == 2700
    assert logg == 4.5


def test_choose_norm_band_prefers_visible_band() -> None:
    selected = choose_norm_band({"Jmag": [1.0, 2.0, 3.0], "Gmag": [2.0, 3.0, 4.0]})
    assert selected == "Gmag"
