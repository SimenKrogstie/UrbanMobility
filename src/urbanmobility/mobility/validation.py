"""Check input assumptions"""

import geopandas as gpd
import pandas as pd

from ..buildings.validation import (
    validate_geodataframe,
    validate_columns,
    validate_indicators,
    validate_districts_exist,
)

__all__ = [
    "validate_geodataframe",
    "validate_columns",
    "validate_indicators",
    "validate_districts_exist",
    "validate_mobility_data",
    "validate_timeprofile_data",
]


def validate_mobility_data(
    districts_gdf: gpd.GeoDataFrame,
    trips_df: pd.DataFrame,
    population_col: str,
    district_col: str,
    start_col: str,
    end_col: str,
) -> None:
    """Validate data used for mobility indicator calculation."""

    validate_geodataframe(districts_gdf, "districts")
    validate_columns(districts_gdf, [district_col, population_col], "districts")
    validate_columns(trips_df, [start_col, end_col], "trips_df")


def validate_timeprofile_data(
    trips_df: pd.DataFrame,
    start_col: str,
    end_col: str,
    time_column: str,
) -> None:
    """Validate data used for time-profile plots."""

    validate_columns(trips_df, [start_col, end_col, time_column], "trips_df")
