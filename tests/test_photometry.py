import pandas as pd

from general_sed import flux_wavel_dict


def test_flux_wavel_dict_uses_available_bands() -> None:
    df = pd.DataFrame(
        [
            {
                "Name": "Test",
                "Av": 0.1,
                "Gmag": 10.0,
                "e_Gmag": 0.02,
                "BPmag": 10.4,
                "e_BPmag": 0.03,
            }
        ]
    )

    result = flux_wavel_dict(df)

    assert set(result) == {"BPmag", "Gmag"}
    assert result["Gmag"][1] > 0
    assert result["Gmag"][2] >= 0
