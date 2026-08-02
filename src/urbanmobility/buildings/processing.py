"""Fetch and transform raw building data"""

import geopandas as gpd
import pandas as pd
import osmnx as ox

from ..config import DEFAULT_CRS, BUILDING_AREA, BUILDING_COUNT
from ..spatial.crs import CRS
from ..spatial.joins import join_buildings_to_districts
from validation import validate_districts


def get_osm_buildings(
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

    # Ensure building crs
    buildings = CRS(buildings, DEFAULT_CRS, name="buildings", wgs84_missing=True)

    # Assign buildings to districts
    buildings = join_buildings_to_districts(buildings, districts, district_col)

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


def _aggregate_building_statistics(
    buildings: gpd.GeoDataFrame,
    district_col: str,
) -> pd.DataFrame:

    buildings = buildings.copy()

    buildings[BUILDING_AREA] = buildings.geometry.area

    return (
        buildings.groupby(district_col)
        .agg(
            **{
                BUILDING_COUNT: ("geometry", "size"),
                BUILDING_AREA: (BUILDING_AREA, "sum"),
            }
        )
        .reset_index()
    )


def get_available_building_types(
    buildings: gpd.GeoDataFrame,
    type_col: str,
    requested_types: list[str] | None = None,
) -> list[str]:
    """
    Return valid buildingtypes available in the dataset.
    """

    available_types = buildings[type_col].value_counts()

    if requested_types is None:
        types = list(available_types.index)

    else:
        types = [t for t in requested_types if t in available_types.index]

    if not types:
        raise ValueError("No building types available for plotting.")
    return types
