import math

import geopandas as gpd
import pytest
from shapely.geometry import Point

from urbanmobility.mobility.metrics import add_mobility_metrics, aggregate_trip_counts
from urbanmobility.config import (
    AREA_KM2,
    DEFAULT_CRS,
    NET_TRIPS,
    NET_TRIPS_PER_CAPITA,
    NET_TRIPS_PER_KM2,
    POPULATION_DENSITY,
    TOTAL_TRIPS,
    TOTAL_TRIPS_PER_CAPITA,
    TOTAL_TRIPS_PER_KM2,
    TRIPS_ENDED,
    TRIPS_ENDED_PER_CAPITA,
    TRIPS_ENDED_PER_KM2,
    TRIPS_STARTED,
    TRIPS_STARTED_PER_CAPITA,
    TRIPS_STARTED_PER_KM2,
)

# Matches tests/conftest.py's trips_df fixture: started A=3 B=4, ended A=2 B=5.
EXPECTED_STARTED_A, EXPECTED_STARTED_B = 3, 4
EXPECTED_ENDED_A, EXPECTED_ENDED_B = 2, 5


# --- aggregate_trip_counts ----------------------------------------------------


def test_aggregate_trip_counts_counts_started_and_ended(trips_df):
    started, ended = aggregate_trip_counts(trips_df, "start_district", "end_district")

    assert started["A"] == EXPECTED_STARTED_A
    assert started["B"] == EXPECTED_STARTED_B
    assert ended["A"] == EXPECTED_ENDED_A
    assert ended["B"] == EXPECTED_ENDED_B


def test_aggregate_trip_counts_series_names(trips_df):
    started, ended = aggregate_trip_counts(trips_df, "start_district", "end_district")

    assert started.name == TRIPS_STARTED
    assert ended.name == TRIPS_ENDED


def test_aggregate_trip_counts_omits_districts_with_no_trips(trips_df):
    only_within_a = trips_df[
        (trips_df["start_district"] == "A") & (trips_df["end_district"] == "A")
    ]

    started, ended = aggregate_trip_counts(
        only_within_a, "start_district", "end_district"
    )

    assert list(started.index) == ["A"]
    assert list(ended.index) == ["A"]


def test_aggregate_trip_counts_handles_empty_input(trips_df):
    empty = trips_df.iloc[0:0]

    started, ended = aggregate_trip_counts(empty, "start_district", "end_district")

    assert len(started) == 0
    assert len(ended) == 0


# --- add_mobility_metrics ------------------------------------------------------


def test_add_mobility_metrics_computes_expected_values(
    mobility_districts_gdf, trips_df
):
    started, ended = aggregate_trip_counts(trips_df, "start_district", "end_district")
    districts = mobility_districts_gdf.set_index("bydel")[
        ["geometry", "befolkning_2024"]
    ].join([started, ended])
    districts[[TRIPS_STARTED, TRIPS_ENDED]] = districts[
        [TRIPS_STARTED, TRIPS_ENDED]
    ].fillna(0)

    result = add_mobility_metrics(districts, "befolkning_2024")

    assert result.loc["A", AREA_KM2] == pytest.approx(1.0)
    assert result.loc["A", POPULATION_DENSITY] == pytest.approx(2000.0)
    assert result.loc["A", NET_TRIPS] == pytest.approx(-1)
    assert result.loc["A", TOTAL_TRIPS] == pytest.approx(5)
    assert result.loc["A", TRIPS_STARTED_PER_KM2] == pytest.approx(3.0)
    assert result.loc["A", TRIPS_ENDED_PER_KM2] == pytest.approx(2.0)
    assert result.loc["A", NET_TRIPS_PER_KM2] == pytest.approx(-1.0)
    assert result.loc["A", TOTAL_TRIPS_PER_KM2] == pytest.approx(5.0)
    assert result.loc["A", TRIPS_STARTED_PER_CAPITA] == pytest.approx(3 / 2000)
    assert result.loc["A", TRIPS_ENDED_PER_CAPITA] == pytest.approx(2 / 2000)
    assert result.loc["A", NET_TRIPS_PER_CAPITA] == pytest.approx(-1 / 2000)
    assert result.loc["A", TOTAL_TRIPS_PER_CAPITA] == pytest.approx(5 / 2000)

    assert result.loc["B", AREA_KM2] == pytest.approx(0.5)
    assert result.loc["B", POPULATION_DENSITY] == pytest.approx(3000.0)
    assert result.loc["B", NET_TRIPS] == pytest.approx(1)
    assert result.loc["B", TOTAL_TRIPS] == pytest.approx(9)
    assert result.loc["B", TRIPS_STARTED_PER_KM2] == pytest.approx(8.0)
    assert result.loc["B", TRIPS_ENDED_PER_KM2] == pytest.approx(10.0)
    assert result.loc["B", TRIPS_STARTED_PER_CAPITA] == pytest.approx(4 / 1500)


def test_add_mobility_metrics_zero_trips_gives_zero_not_nan(mobility_districts_gdf):
    districts = mobility_districts_gdf.set_index("bydel").copy()
    districts[TRIPS_STARTED] = 0
    districts[TRIPS_ENDED] = 0

    result = add_mobility_metrics(districts, "befolkning_2024")

    assert result.loc["A", NET_TRIPS] == 0
    assert result.loc["A", TOTAL_TRIPS] == 0
    assert result.loc["A", TRIPS_STARTED_PER_KM2] == 0
    assert result.loc["A", TRIPS_STARTED_PER_CAPITA] == 0
    assert not math.isnan(result.loc["A", TRIPS_STARTED_PER_CAPITA])


def test_add_mobility_metrics_zero_population_divides_to_inf(mobility_districts_gdf):
    districts = mobility_districts_gdf.set_index("bydel").copy()
    districts["befolkning_2024"] = [0, 1500]
    districts[TRIPS_STARTED] = [3, 4]
    districts[TRIPS_ENDED] = [2, 5]

    result = add_mobility_metrics(districts, "befolkning_2024")

    # population_density is population/area, so zero population gives 0, not inf.
    assert result.loc["A", POPULATION_DENSITY] == 0
    assert math.isinf(result.loc["A", TRIPS_STARTED_PER_CAPITA])
    assert math.isinf(result.loc["A", TRIPS_ENDED_PER_CAPITA])


def test_add_mobility_metrics_zero_area_district_divides_to_inf():
    # Points have zero area but are valid, non-empty geometries.
    districts = gpd.GeoDataFrame(
        {
            "bydel": ["A"],
            "befolkning_2024": [1000],
            TRIPS_STARTED: [3],
            TRIPS_ENDED: [2],
        },
        geometry=[Point(0, 0)],
        crs=DEFAULT_CRS,
    ).set_index("bydel")

    result = add_mobility_metrics(districts, "befolkning_2024")  # type: ignore[arg-type]

    assert math.isinf(result.loc["A", POPULATION_DENSITY])
    assert math.isinf(result.loc["A", TRIPS_STARTED_PER_KM2])
