def test_buildings_public_api():
    from urbanmobility import buildings

    assert callable(buildings.fetch_buildings)
    assert callable(buildings.calculate_building_indicators)
    assert callable(buildings.plot_building_indicators)
    assert callable(buildings.plot_building_types)

def test_buildings_exports():
    from urbanmobility import buildings

    assert set(buildings.__all__) == {
        "fetch_buildings",
        "calculate_building_indicators",
        "plot_building_indicators",
        "plot_building_types",
    }