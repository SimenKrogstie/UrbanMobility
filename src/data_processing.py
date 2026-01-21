import geopandas as gpd
import pandas as pd
import osmnx as ox
from helpers import CRS


def points_gdf(
        trips_df: pd.DataFrame,
        lat_col: str,
        lon_col: str,
        source_crs: str = "EPSG:4326",
        target_crs: str = "EPSG:25833",
    ) -> gpd.GeoDataFrame:
    """
    Converts a DataFrame with coordinates to a GeoDataFrame with Shapely Point geometries.

    The function:
    1. Checks that the necessary coordinate columns exist.
    2. Creates Shapely Point geometries from the longitude/latitude columns.
    3. Sets the source CRS.
    4. Transforms the geometry to the target CRS.


    Parameters
    ----------
    trips_df : pd.DataFrame
        DataFrame that contains coordinate columns.
    lat_col: str
        Name of the column with latitude.
    lon_col: str
        Name of the column with longitude.
    source_crs : str, optional
        CRS of the input coordinates.
        Default is "EPSG:4326" (WGS84).
    target_crs: str, optional
        CRS to transform to after geometry creation.
        Default is "EPSG:25833".

    Returns
    -------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with point geometries and CRS set to "target_crs".
    
    Raises
    ------
    KeyError
        If either "lat_col" or "lon_col" does not exist in "trips_df".
    ValueError
        If the transformation to "target_crs" fails.

    """
    # Checks that both coordinate columns exist in trips_df
    if lat_col not in trips_df.columns or lon_col not in trips_df.columns:
        raise KeyError(f"{trips_df} is missing the columns {lat_col!r} and/or {lon_col!r}.")

    # Makes a GeoDataFrame based on trips_df
    gdf = gpd.GeoDataFrame(
        trips_df.copy(),
        geometry=gpd.points_from_xy(trips_df[lon_col], trips_df[lat_col]),
        crs=source_crs
    )

    # Transforms to target_crs
    try:
        return gdf.to_crs(target_crs)
    except Exception as e:
        raise ValueError(f"Could not transform CRS to {target_crs}: {e}")


def add_district(
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


def fetch_buildings(
    districts_gdf: gpd.GeoDataFrame,
    district_col: str = "bydel",
    query: str = "Oslo, Norway",
    tags: dict | None = None,
) -> gpd.GeoDataFrame:
    """
    Retrieves buildings from OpenStreetMap (OSM) and associates them with districts
    using a spatial join.

    The function:
    1. Validates that "districts_gdf" has the required CRS and columns.
    2. Ensures that "districts_gdf" has a valid CRS and reprojects it to "EPSG:25833".
    3. Fetches buildings from OSM based on the query and tags.
    4. Filters to keep only Polygon/MultiPolygon geometries.
    5. Reprojects buildings to the same CRS as "districts_gdf".
    6. Performs a spatial join to determine which district each building belongs to.

    Parameters
    ----------
    districts_gdf : gpd.GeoDataFrame
        GeoDataFrame with shapely Polygon/Multipolygon geometries representing districts.
    district_col : str, optional
        Name of the column in "districts_gdf" that contains district names.
        Default is "bydel"
    query : str, optional
        Place name used by OSM to retrieve buildings.
        Default is "Oslo, Norway".
    tags : dict or None, optional
        OSM tag filters.
        Default is "{"building": True}".

    Returns
    -------
    buildings_in_districts : gpd.GeoDataFrame
        GeoDataFrame with buildings from OSM reprojected to "EPSG:25833".
        Contains building geometries and district names.
    
    Raises
    ------
    KeyError
        If "district_col" does not exist in "districts_gdf".
    ValueError
        If "districts_gdf" lacks CRS or CRS transformation fails.
    """
    target_crs = "EPSG:25833"

    # Retrieve all types of buildings from OpenStreetMap.
    if tags is None:
        tags = {"building": True}

    # Check that district_col exists in districts_gdf
    if district_col not in districts_gdf.columns:
        raise KeyError(f"The column {district_col!r} does not exist in districts_gdf.")
    if "geometry" not in districts_gdf.columns:
        raise ValueError("districts_gdf lacks a 'geometry' column.")

    # Ensure that districts_gdf has a valid CRS and reproject it to target_crs.
    districts_gdf = CRS(districts_gdf, target_crs, name="districts_gdf")

    # Retrieve buildings from OSM
    buildings = ox.features_from_place(query=query, tags=tags)

    # Keep only Polygon/MultiPolygon geometries
    buildings = buildings[
        buildings.geometry.type.isin(["Polygon", "MultiPolygon"])
    ].copy()

    # Reprojects buildings to target_crs
    buildings = CRS(buildings, target_crs, name="buildings", wgs84_mangler=True)

    # Filter columns needed for spatial join
    district_join = districts_gdf[[district_col, "geometry"]]

    # Find the district each building belongs to with spatial join
    buildings_in_districts = gpd.sjoin(
        buildings,
        district_join,
        how="left",
        predicate="within",
    ).drop(columns=["index_right"])

    return buildings_in_districts