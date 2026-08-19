import math

import pandas as pd
import pytest

from urbanmobility.mobility.indicators import calculate_mobility_indicators
from urbanmobility.config import (
    AREA_KM2,
    NET_TRIPS,
    POPULATION_DENSITY,
    TOTAL_TRIPS,
    TRIPS_ENDED,
    TRIPS_STARTED,
    TRIPS_STARTED_PER_CAPITA,
    TRIPS_STARTED_PER_KM2,
)

# Matches tests/conftest.py's mobility_districts_gdf/trips_df fixtures: started
# A=3 B=4, ended A=2 B=5, population A=2000 B=1500, area A=1km^2 B=0.5km^2.
EXPECTED_STARTED_A, EXPECTED_STARTED_B = 3, 4
EXPECTED_ENDED_A, EXPECTED_ENDED_B = 2, 5


def test_calculate_mobility_indicators_computes_expected_values(
    mobility_districts_gdf, trips_df
):
    result = calculate_mobility_indicators(mobility_districts_gdf, trips_df)

    assert result.loc["A", TRIPS_STARTED] == EXPECTED_STARTED_A
    assert result.loc["A", TRIPS_ENDED] == EXPECTED_ENDED_A
    assert result.loc["A", NET_TRIPS] == -1
    assert result.loc["A", TOTAL_TRIPS] == 5
    assert result.loc["A", AREA_KM2] == pytest.approx(1.0)
    assert result.loc["A", POPULATION_DENSITY] == pytest.approx(2000.0)
    assert result.loc["A", TRIPS_STARTED_PER_KM2] == pytest.approx(3.0)
    assert result.loc["A", TRIPS_STARTED_PER_CAPITA] == pytest.approx(3 / 2000)

    assert result.loc["B", TRIPS_STARTED] == EXPECTED_STARTED_B
    assert result.loc["B", TRIPS_ENDED] == EXPECTED_ENDED_B
    assert result.loc["B", NET_TRIPS] == 1
    assert result.loc["B", TOTAL_TRIPS] == 9
    assert result.loc["B", AREA_KM2] == pytest.approx(0.5)
    assert result.loc["B", POPULATION_DENSITY] == pytest.approx(3000.0)
    assert result.loc["B", TRIPS_STARTED_PER_KM2] == pytest.approx(8.0)
    assert result.loc["B", TRIPS_STARTED_PER_CAPITA] == pytest.approx(4 / 1500)


def test_calculate_mobility_indicators_district_with_no_trips_fills_zero(
    mobility_districts_gdf, trips_df
):
    only_within_a = trips_df[
        (trips_df["start_district"] == "A") & (trips_df["end_district"] == "A")
    ]

    result = calculate_mobility_indicators(mobility_districts_gdf, only_within_a)

    assert result.loc["B", TRIPS_STARTED] == 0
    assert result.loc["B", TRIPS_ENDED] == 0
    assert result.loc["B", NET_TRIPS] == 0
    assert result.loc["B", TOTAL_TRIPS] == 0
    assert not math.isnan(result.loc["B", TOTAL_TRIPS])


def test_calculate_mobility_indicators_indexes_by_district_col(
    mobility_districts_gdf, trips_df
):
    result = calculate_mobility_indicators(mobility_districts_gdf, trips_df)

    assert result.index.name == "bydel"
    assert set(result.index) == {"A", "B"}


def test_calculate_mobility_indicators_rejects_non_geodataframe_districts(trips_df):
    with pytest.raises(TypeError):
        calculate_mobility_indicators(
            pd.DataFrame({"bydel": ["A"], "befolkning_2024": [1000]}),  # type: ignore[arg-type]
            trips_df,
        )


def test_calculate_mobility_indicators_rejects_missing_population_col(
    mobility_districts_gdf, trips_df
):
    districts = mobility_districts_gdf.drop(columns=["befolkning_2024"])

    with pytest.raises(KeyError):
        calculate_mobility_indicators(districts, trips_df)


def test_calculate_mobility_indicators_rejects_missing_start_col(
    mobility_districts_gdf, trips_df
):
    trips = trips_df.drop(columns=["start_district"])

    with pytest.raises(KeyError):
        calculate_mobility_indicators(mobility_districts_gdf, trips)


def test_calculate_mobility_indicators_rejects_invalid_district_geometry(
    invalid_geometry_gdf, trips_df
):
    districts = invalid_geometry_gdf.copy()
    districts["befolkning_2024"] = [1000]

    with pytest.raises(ValueError):
        calculate_mobility_indicators(districts, trips_df)


def test_calculate_mobility_indicators_is_crs_independent(
    mobility_districts_gdf, trips_df
):
    districts_wgs84 = mobility_districts_gdf.to_crs("EPSG:4326")

    result = calculate_mobility_indicators(districts_wgs84, trips_df)

    assert result.loc["A", AREA_KM2] == pytest.approx(1.0, rel=1e-3)
    assert result.loc["B", AREA_KM2] == pytest.approx(0.5, rel=1e-3)
    assert result.loc["A", TRIPS_STARTED] == EXPECTED_STARTED_A
    assert result.loc["B", TRIPS_STARTED] == EXPECTED_STARTED_B
