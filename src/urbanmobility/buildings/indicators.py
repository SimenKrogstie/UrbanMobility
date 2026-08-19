"""Calculate building indicators from building and district data."""

import geopandas as gpd

from .validation import validate_building_data
from .metrics import aggregate_building_statistics, add_building_metrics
from ..spatial.crs import CRS
from ..config import (
    DEFAULT_CRS,
    BUILDING_COUNT,
    BUILDING_AREA,
)


def calculate_building_indicators(
    buildings_gdf: gpd.GeoDataFrame,
    districts_gdf: gpd.GeoDataFrame,
    district_col: str = "bydel",
) -> gpd.GeoDataFrame:

    # Validate data and transform CRS
    validate_building_data(buildings_gdf, districts_gdf, district_col)
    buildings = CRS(buildings_gdf, DEFAULT_CRS, name="buildings")
    districts = CRS(districts_gdf, DEFAULT_CRS, name="districts")

    # Compute building metrics
    buildings_stats = aggregate_building_statistics(
        buildings,
        district_col,
    )

    districts = districts.merge(
        buildings_stats,
        on=district_col,
        how="left",
    )

    districts[[BUILDING_COUNT, BUILDING_AREA]] = districts[
        [BUILDING_COUNT, BUILDING_AREA]
    ].fillna(0)

    districts = add_building_metrics(districts)

    return districts.set_index(district_col)
