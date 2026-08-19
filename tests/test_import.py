import urbanmobility


def test_public_api():
    assert urbanmobility.__version__ == "0.1.0"
    assert urbanmobility.DEFAULT_CRS is not None
    assert urbanmobility.CRS_WGS84 is not None
