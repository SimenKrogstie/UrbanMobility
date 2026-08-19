"""Pure numeric calculations for mobility indicators."""

import geopandas as gpd
import pandas as pd

from ..config import (
    AREA_KM2,
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


def aggregate_trip_counts(
    trips_df: pd.DataFrame,
    start_col: str,
    end_col: str,
) -> tuple[pd.Series, pd.Series]:
    """Counts trips started and ended per district."""

    started = trips_df.groupby(start_col).size().rename(TRIPS_STARTED)
    ended = trips_df.groupby(end_col).size().rename(TRIPS_ENDED)

    return started, ended


def add_mobility_metrics(
    districts: gpd.GeoDataFrame,
    population_col: str,
) -> gpd.GeoDataFrame:
    """Computes area, density, and trip-based indicators for each district."""

    districts[AREA_KM2] = districts.geometry.area / 1_000_000
    districts[POPULATION_DENSITY] = districts[population_col] / districts[AREA_KM2]

    districts[NET_TRIPS] = districts[TRIPS_ENDED] - districts[TRIPS_STARTED]
    districts[TOTAL_TRIPS] = districts[TRIPS_STARTED] + districts[TRIPS_ENDED]

    districts[TRIPS_STARTED_PER_KM2] = districts[TRIPS_STARTED] / districts[AREA_KM2]
    districts[TRIPS_ENDED_PER_KM2] = districts[TRIPS_ENDED] / districts[AREA_KM2]
    districts[NET_TRIPS_PER_KM2] = districts[NET_TRIPS] / districts[AREA_KM2]
    districts[TOTAL_TRIPS_PER_KM2] = districts[TOTAL_TRIPS] / districts[AREA_KM2]

    districts[TRIPS_STARTED_PER_CAPITA] = (
        districts[TRIPS_STARTED] / districts[population_col]
    )
    districts[TRIPS_ENDED_PER_CAPITA] = (
        districts[TRIPS_ENDED] / districts[population_col]
    )
    districts[NET_TRIPS_PER_CAPITA] = districts[NET_TRIPS] / districts[population_col]
    districts[TOTAL_TRIPS_PER_CAPITA] = (
        districts[TOTAL_TRIPS] / districts[population_col]
    )

    return districts
