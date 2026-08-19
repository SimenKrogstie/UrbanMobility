import pandas as pd
import pytest

from urbanmobility.mobility.validation import (
    validate_mobility_data,
    validate_timeprofile_data,
)


# --- validate_mobility_data ---------------------------------------------------


def test_validate_mobility_data_rejects_non_geodataframe_districts(trips_df):
    with pytest.raises(TypeError):
        validate_mobility_data(
            pd.DataFrame({"bydel": ["A"], "befolkning_2024": [1000]}),  # type: ignore[arg-type]
            trips_df,
            "befolkning_2024",
            "bydel",
            "start_district",
            "end_district",
        )


def test_validate_mobility_data_rejects_missing_district_col(
    mobility_districts_gdf, trips_df
):
    districts = mobility_districts_gdf.rename(columns={"bydel": "not_bydel"})
    with pytest.raises(KeyError, match="bydel"):
        validate_mobility_data(
            districts,
            trips_df,
            "befolkning_2024",
            "bydel",
            "start_district",
            "end_district",
        )


def test_validate_mobility_data_rejects_missing_population_col(
    mobility_districts_gdf, trips_df
):
    districts = mobility_districts_gdf.drop(columns=["befolkning_2024"])
    with pytest.raises(KeyError, match="befolkning_2024"):
        validate_mobility_data(
            districts,
            trips_df,
            "befolkning_2024",
            "bydel",
            "start_district",
            "end_district",
        )


def test_validate_mobility_data_rejects_missing_start_col(
    mobility_districts_gdf, trips_df
):
    trips = trips_df.drop(columns=["start_district"])
    with pytest.raises(KeyError, match="start_district"):
        validate_mobility_data(
            mobility_districts_gdf,
            trips,
            "befolkning_2024",
            "bydel",
            "start_district",
            "end_district",
        )


def test_validate_mobility_data_rejects_missing_end_col(
    mobility_districts_gdf, trips_df
):
    trips = trips_df.drop(columns=["end_district"])
    with pytest.raises(KeyError, match="end_district"):
        validate_mobility_data(
            mobility_districts_gdf,
            trips,
            "befolkning_2024",
            "bydel",
            "start_district",
            "end_district",
        )


def test_validate_mobility_data_rejects_invalid_district_geometry(
    invalid_geometry_gdf, trips_df
):
    districts = invalid_geometry_gdf.copy()
    districts["befolkning_2024"] = [1000]
    with pytest.raises(ValueError):
        validate_mobility_data(
            districts,
            trips_df,
            "befolkning_2024",
            "bydel",
            "start_district",
            "end_district",
        )


def test_validate_mobility_data_passes_for_valid_input(
    mobility_districts_gdf, trips_df
):
    validate_mobility_data(
        mobility_districts_gdf,
        trips_df,
        "befolkning_2024",
        "bydel",
        "start_district",
        "end_district",
    )


# --- validate_timeprofile_data ------------------------------------------------


def test_validate_timeprofile_data_rejects_missing_start_col(trips_df):
    trips = trips_df.drop(columns=["start_district"])
    with pytest.raises(KeyError, match="start_district"):
        validate_timeprofile_data(trips, "start_district", "end_district", "started_at")


def test_validate_timeprofile_data_rejects_missing_end_col(trips_df):
    trips = trips_df.drop(columns=["end_district"])
    with pytest.raises(KeyError, match="end_district"):
        validate_timeprofile_data(trips, "start_district", "end_district", "started_at")


def test_validate_timeprofile_data_rejects_missing_time_column(trips_df):
    trips = trips_df.drop(columns=["started_at"])
    with pytest.raises(KeyError, match="started_at"):
        validate_timeprofile_data(trips, "start_district", "end_district", "started_at")


def test_validate_timeprofile_data_passes_for_valid_input(trips_df):
    validate_timeprofile_data(trips_df, "start_district", "end_district", "started_at")
