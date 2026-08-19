import math

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from urbanmobility.buildings.indicators import calculate_building_indicators
from urbanmobility.config import (
    BUILDING_COUNT,
    BUILDING_AREA,
    BUILDING_DENSITY,
    BUILT_AREA_PERCENT,
    AVG_BUILDING_AREA,
    DEFAULT_CRS,
)

# Matches tests/conftest.py fixture geometry (see test_buildings_metrics.py).
EXPECTED_AREA_A = 20 * 20 + 30 * 30
EXPECTED_AREA_B = 50 * 50


def test_calculate_building_indicators_computes_expected_values(
    buildings_gdf, districts_gdf
):
    result = calculate_building_indicators(buildings_gdf, districts_gdf)

    assert result.loc["A", BUILDING_COUNT] == 2
    assert result.loc["A", BUILDING_AREA] == pytest.approx(EXPECTED_AREA_A)
    assert result.loc["A", BUILDING_DENSITY] == pytest.approx(2.0)
    assert result.loc["A", BUILT_AREA_PERCENT] == pytest.approx(0.13)
    assert result.loc["A", AVG_BUILDING_AREA] == pytest.approx(650.0)

    assert result.loc["B", BUILDING_COUNT] == 1
    assert result.loc["B", BUILDING_AREA] == pytest.approx(EXPECTED_AREA_B)
    assert result.loc["B", BUILDING_DENSITY] == pytest.approx(2.0)
    assert result.loc["B", BUILT_AREA_PERCENT] == pytest.approx(0.5)
    assert result.loc["B", AVG_BUILDING_AREA] == pytest.approx(2500.0)


def test_calculate_building_indicators_district_with_no_buildings_fills_zero(
    buildings_gdf, districts_gdf
):
    only_a = buildings_gdf[buildings_gdf["bydel"] == "A"]

    result = calculate_building_indicators(only_a, districts_gdf)

    assert result.loc["B", BUILDING_COUNT] == 0
    assert result.loc["B", BUILDING_AREA] == 0
    assert result.loc["B", BUILDING_DENSITY] == 0
    assert result.loc["B", BUILT_AREA_PERCENT] == 0
    assert result.loc["B", AVG_BUILDING_AREA] == 0
    assert not math.isnan(result.loc["B", AVG_BUILDING_AREA])


def test_calculate_building_indicators_drops_buildings_in_unknown_district(
    buildings_gdf, districts_gdf
):
    stray_building = gpd.GeoDataFrame(
        {"bydel": ["C"]},
        geometry=[box(590000, 6640000, 590010, 6640010)],
        crs=DEFAULT_CRS,
    )
    buildings_with_stray = gpd.GeoDataFrame(
        pd.concat([buildings_gdf, stray_building], ignore_index=True)
    )

    result = calculate_building_indicators(buildings_with_stray, districts_gdf)

    assert "C" not in result.index
    assert result.loc["A", BUILDING_COUNT] == 2
    assert result.loc["B", BUILDING_COUNT] == 1


def test_calculate_building_indicators_indexes_by_district_col(
    buildings_gdf, districts_gdf
):
    result = calculate_building_indicators(buildings_gdf, districts_gdf)

    assert result.index.name == "bydel"
    assert set(result.index) == {"A", "B"}


def test_calculate_building_indicators_rejects_non_geodataframe_buildings(
    districts_gdf,
):
    with pytest.raises(TypeError):
        calculate_building_indicators(
            pd.DataFrame({"bydel": ["A"]}),  # type: ignore[arg-type]
            districts_gdf,
        )


def test_calculate_building_indicators_rejects_missing_district_col(
    buildings_gdf, districts_gdf
):
    buildings = buildings_gdf.rename(columns={"bydel": "not_bydel"})

    with pytest.raises(KeyError):
        calculate_building_indicators(buildings, districts_gdf)


def test_calculate_building_indicators_rejects_invalid_district_geometry(
    buildings_gdf, invalid_geometry_gdf
):
    with pytest.raises(ValueError):
        calculate_building_indicators(buildings_gdf, invalid_geometry_gdf)


def test_calculate_building_indicators_is_crs_independent(buildings_gdf, districts_gdf):
    buildings_wgs84 = buildings_gdf.to_crs("EPSG:4326")
    districts_wgs84 = districts_gdf.to_crs("EPSG:4326")

    result = calculate_building_indicators(buildings_wgs84, districts_wgs84)

    assert result.loc["A", BUILDING_COUNT] == 2
    assert result.loc["A", BUILDING_AREA] == pytest.approx(EXPECTED_AREA_A, rel=1e-6)
    assert result.loc["B", BUILDING_AREA] == pytest.approx(EXPECTED_AREA_B, rel=1e-6)
