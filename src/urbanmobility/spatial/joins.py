import geopandas as gpd
import pandas as pd
from .crs import CRS

def add_trip_districts(
        trips_df: pd.DataFrame,
        start_gdf: gpd.GeoDataFrame,
        end_gdf: gpd.GeoDataFrame,
        districts_gdf: gpd.GeoDataFrame,
        district_col: str = "bydel",
    ) -> pd.DataFrame:
    """
    Adds columns with district names for start and end points based on spatial join.

    The function:
    1. Verifies that the district geometry has CRS and that the district column exists.
    2. Reprojects start and end points to the same CRS as the district polygons.
    3. Performs spatial join for both point sets.
    4. Returns a DataFrame with two new columns: "start_district" and "end_district".

    Parameters
    ----------
    trips_df : pd.DataFrame
        The original DataFrame with trip data (without geometry).
    start_gdf : gpd.GeoDataFrame
        GeoDataFrame with point geometries for start positions.
    end_gdf : gpd.GeoDataFrame
        GeoDataFrame with point geometries for end positions.
    districts_gdf : gpd.GeoDataFrame
        GeoDataFrame with shapely Polygon/Multipolygon geometries for districts.
    district_col : str, optional
        Name of the column in "districts_gdf" that contains district names.
        Default is "bydel". 
   
    Returns
    -------
    trips : pd.DataFrame
        A copy of "trips_df" with two new columns: "start_district" and "end_district".

    Raises
    ------
    KeyError
        If "district_col" does not exist in "districts_gdf".
    ValueError
        If "districts_gdf" lacks CRS or CRS transformation fails.
    """

    # Checks if district_col exists in districts_gdf
    if district_col not in districts_gdf.columns:
        raise KeyError(f"districts_gdf is missing the column {district_col!r}.")

    # Checks that districts_gdf has a valid CRS
    districts_gdf = CRS(districts_gdf, str(districts_gdf.crs), name="districts_gdf")
    
    # Reprojects start and end points to the same CRS as districts.
    start_gdf = CRS(start_gdf, str(districts_gdf.crs), name="start_gdf")
    end_gdf = CRS(end_gdf, str(districts_gdf.crs), name="end_gdf")

    # Spatial join for start points
    start_join = gpd.sjoin(
        start_gdf,
        districts_gdf[[district_col, "geometry"]],
        how="left",
        predicate="within"
    ).rename(columns={district_col: "start_district"})

    # Spatial join for end points
    end_join = gpd.sjoin(
        end_gdf,
        districts_gdf[[district_col, "geometry"]],
        how="left",
        predicate="within"
    ).rename(columns={district_col: "end_district"})

    # Add new columns to trips_df
    trips = trips_df.copy()
    trips["start_district"] = start_join["start_district"].values
    trips["end_district"] = end_join["end_district"].values

    return trips


def join_buildings_to_districts(
    buildings,
    districts,
    district_col,
):
    district_join = districts[[district_col, "geometry"]]

    return (
        gpd.sjoin(
            buildings,
            district_join,
            how="left",
            predicate="within",
        )
        .drop(columns=["index_right"])
    )