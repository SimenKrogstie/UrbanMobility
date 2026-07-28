"""Fetch and transform raw building data"""

import geopandas as gpd
import pandas as pd
import osmnx as ox

from ..config import DEFAULT_CRS
from ..spatial.crs import CRS
from ..spatial.joins import join_buildings_to_districts
from .constants import *
from validation import validate_districts


def fetch_buildings(
    districts_gdf: gpd.GeoDataFrame,
    district_col: str = "bydel",
    query: str = "Oslo, Norway",
    tags: dict | None = None,
) -> gpd.GeoDataFrame:
    """
    Retrieves buildings from OpenStreetMap (OSM) and assign them to districts.

    Parameters
    ----------
    districts_gdf : gpd.GeoDataFrame
        District Polygon/Multipolygon with a district identifier column.
    district_col : str, defaul="bydel"
        Column containing district names.
    query : str, default="Oslo, Norway"
        Place name used for OpenStreetmap query.
    tags : dict | None, 
        OSM tags used to filter features
        Defaults to "{"building": True}".

    Returns
    -------
    gpd.GeoDataFrame
        Building polygons with associated district information.
    """

    if tags is None:
        tags = {"building": True}

    # Validate district input
    validate_districts(districts_gdf, district_col)

    # Ensure districts use project CRS
    districts = CRS(districts_gdf, DEFAULT_CRS, name="districts_gdf")

    # Retrieve buildings from OSM
    buildings = ox.features_from_place(query=query, tags=tags)

    # Keep only Polygon/MultiPolygon building geometries

    buildings = _filter_building_geometries(buildings)

    buildings = buildings[
        buildings.geometry.type.isin(["Polygon", "MultiPolygon"])
    ].copy()

    # Ensure building crs
    buildings = CRS(buildings, DEFAULT_CRS, name="buildings", wgs84_missing=True)

    # Assign buildings to districts
    buildings = join_buildings_to_districts(
        buildings,
        districts,
        district_col
    )

    return buildings


def _filter_building_geometries(
        buildings: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Keep only polgon/multipolygon geometries.

    Parameters
    ----------
    buildings : gpd.GeoDataFrame
        Raw OSM building data.

    Returns
    -------
    gpd.GeoDataFrame
        Buildings containing only Polygon/MultiPolygon geometries.
    """

    return buildings[
        buildings.geometry.type.isin(
            [
                "Polygon",
                "MultiPolygon",
            ]
        )
    ].copy()


def _aggregate_building_metrics(
        buildings: gpd.GeoDataFrame,
        district_col:str,
) -> pd.DataFrame:
    
    buildings = buildings.copy()

    buildings[BUILDING_AREA] = buildings.geometry.area

    return (
        buildings.groupby(district_col)
        .agg(
            num_buildings=("geometry", "size"),
            building_area_m2=("area_m2", "sum")
        )
        .reset_index()
    )