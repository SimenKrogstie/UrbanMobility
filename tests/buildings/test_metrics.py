import math

import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from urbanmobility.buildings.metrics import (
    aggregate_building_statistics,
    add_building_metrics,
)
from urbanmobility.config import (
    AREA_M2,
    AREA_KM2,
    BUILDING_COUNT,
    BUILDING_AREA,
    BUILDING_DENSITY,
    BUILT_AREA_PERCENT,
    AVG_BUILDING_AREA,
    DEFAULT_CRS,
)

# Matches tests/conftest.py fixture geometry: A has a 20x20 and a 30x30
# building (400 + 900 = 1300 m^2), B has a 50x50 building (2500 m^2).
EXPECTED_AREA_A = 20 * 20 + 30 * 30
EXPECTED_AREA_B = 50 * 50


# --- aggregate_building_statistics -----------------------------------------


def test_aggregate_building_statistics_sums_count_and_area(buildings_gdf):
    stats = aggregate_building_statistics(buildings_gdf, "bydel").set_index("bydel")

    assert stats.loc["A", BUILDING_COUNT] == 2
    assert stats.loc["A", BUILDING_AREA] == pytest.approx(EXPECTED_AREA_A)
    assert stats.loc["B", BUILDING_COUNT] == 1
    assert stats.loc["B", BUILDING_AREA] == pytest.approx(EXPECTED_AREA_B)


def test_aggregate_building_statistics_omits_districts_with_no_buildings(
    buildings_gdf,
):
    only_a = buildings_gdf[buildings_gdf["bydel"] == "A"]

    stats = aggregate_building_statistics(only_a, "bydel")

    assert list(stats["bydel"]) == ["A"]


def test_aggregate_building_statistics_handles_empty_input(buildings_gdf):
    empty = buildings_gdf.iloc[0:0]

    stats = aggregate_building_statistics(empty, "bydel")

    assert len(stats) == 0


def test_aggregate_building_statistics_single_building():
    single = gpd.GeoDataFrame(
        {"bydel": ["A"]},
        geometry=[box(0, 0, 10, 10)],
        crs=DEFAULT_CRS,
    )

    stats = aggregate_building_statistics(single, "bydel").set_index("bydel")

    assert stats.loc["A", BUILDING_COUNT] == 1
    assert stats.loc["A", BUILDING_AREA] == pytest.approx(100.0)


# --- add_building_metrics ----------------------------------------------------


def test_add_building_metrics_computes_expected_values(districts_gdf, buildings_gdf):
    stats = aggregate_building_statistics(buildings_gdf, "bydel")
    districts = districts_gdf.merge(stats, on="bydel", how="left").set_index("bydel")

    result = add_building_metrics(districts)

    assert result.loc["A", AREA_M2] == pytest.approx(1_000_000)
    assert result.loc["A", AREA_KM2] == pytest.approx(1.0)
    assert result.loc["A", BUILDING_DENSITY] == pytest.approx(2.0)
    assert result.loc["A", BUILT_AREA_PERCENT] == pytest.approx(0.13)
    assert result.loc["A", AVG_BUILDING_AREA] == pytest.approx(650.0)

    assert result.loc["B", AREA_KM2] == pytest.approx(0.5)
    assert result.loc["B", BUILDING_DENSITY] == pytest.approx(2.0)
    assert result.loc["B", AVG_BUILDING_AREA] == pytest.approx(2500.0)


def test_add_building_metrics_zero_buildings_gives_zero_not_nan(districts_gdf):
    districts = districts_gdf.set_index("bydel").copy()
    districts[BUILDING_COUNT] = 0
    districts[BUILDING_AREA] = 0.0

    result = add_building_metrics(districts)

    assert result.loc["A", BUILDING_DENSITY] == 0
    assert result.loc["A", BUILT_AREA_PERCENT] == 0
    assert result.loc["A", AVG_BUILDING_AREA] == 0
    assert not math.isnan(result.loc["A", AVG_BUILDING_AREA])


def test_add_building_metrics_zero_area_district_divides_to_inf():
    # Points have zero area but are valid, non-empty geometries.
    districts = gpd.GeoDataFrame(
        {
            "bydel": ["A"],
            BUILDING_COUNT: [3],
            BUILDING_AREA: [500.0],
        },
        geometry=[Point(0, 0)],
        crs=DEFAULT_CRS,
    ).set_index("bydel")

    result = add_building_metrics(districts)

    assert math.isinf(result.loc["A", BUILDING_DENSITY])
    assert math.isinf(result.loc["A", BUILT_AREA_PERCENT])
