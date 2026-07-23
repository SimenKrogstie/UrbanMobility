import geopandas as gpd
from ..spatial.crs import CRS
import osmnx as ox

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
    buildings = CRS(buildings, target_crs, name="buildings", wgs84_missing=True)

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