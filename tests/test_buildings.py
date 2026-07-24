def test_buildings_public_api():
    from urbanmobility.buildings import (
        fetch_buildings,
        calculate_building_indicators,
        plot_building_indicators,
        plot_building_types,
    )

    assert callable(fetch_buildings)
    assert callable(calculate_building_indicators)
    assert callable(plot_building_indicators)
    assert callable(plot_building_types)