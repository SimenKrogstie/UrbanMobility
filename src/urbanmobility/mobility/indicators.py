import geopandas as gpd
import pandas as pd

from ..config import DEFAULT_CRS, TRIPS_ENDED, TRIPS_STARTED
from ..spatial.crs import CRS
from .metrics import add_mobility_metrics, aggregate_trip_counts
from .validation import validate_mobility_data


def calculate_mobility_indicators(
    districts_gdf: gpd.GeoDataFrame,
    trips_df: pd.DataFrame,
    population_col: str = "befolkning_2024",
    district_col: str = "bydel",
    start_col: str = "start_district",
    end_col: str = "end_district",
) -> gpd.GeoDataFrame:
    """
    Computes mobility and area-based indicators for each district.

    The function:
    1. Ensures valid CRS and geometry in "districts_gdf".
    2. Counts number of trip start and end points per district.
    3. Calculates area, population density, and derived trip metrics for each
       district.

    Parameters
    ----------
    districts_gdf : gpd.GeoDataFrame
        GeoDataFrame with district polygons and population data.
    trips_df : pd.DataFrame
        DataFrame with trip data and start and end districts.
    population_col : str, optional
        Name of the column in "districts_gdf" containing population numbers.
        Default is "befolkning_2024"
    district_col : str, optional
        Name of the column in "districts_gdf" containing district names.
        Default is "bydel".
    start_col : str, optional
        Name of the column in "trips_df" for start district.
        Default is "start_district".
    end_col : str, optional
        Name of the column in "trips_df" for end district.
        Default is "end_district".

    Returns
    -------
    mobility : gpd.GeoDataFrame
        GeoDataFrame indexed on "district_col" containing:
        - geometry
        - area (km^2)
        - population and population density
        - trips started / ended
        - trips per km^2 and per capita
        - net and total number of trips

    Raises
    ------
    KeyError
        If required columns are missing in "districts_gdf" or "trips_df".
    ValueError
        If "districts_gdf" lacks CRS or CRS transformation fails.
    """

    validate_mobility_data(
        districts_gdf, trips_df, population_col, district_col, start_col, end_col
    )

    districts = CRS(districts_gdf, DEFAULT_CRS, name="districts_gdf")

    started, ended = aggregate_trip_counts(trips_df, start_col, end_col)

    mobility = districts.set_index(district_col)[["geometry", population_col]].join(
        [started, ended]
    )
    mobility[[TRIPS_STARTED, TRIPS_ENDED]] = mobility[
        [TRIPS_STARTED, TRIPS_ENDED]
    ].fillna(0)

    return add_mobility_metrics(mobility, population_col)
