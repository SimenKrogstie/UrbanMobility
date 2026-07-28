"""Check input assumptions"""

import geopandas as gpd

def _validate_geodataframe (
        gdf: gpd.GeoDataFrame,
        name: str,
) -> None:
    """Validate that the input is a GeoDataFrame"""

    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError(
            f"{name} must be a GeoDataFrame"
        )


def _validate_geometry(
          gdf: gpd.GeoDataFrame,
          name: str,
) -> None:
    """Validate geomtry column and geometries"""

    if "geometry" not in gdf.columns:
        raise ValueError(
            f"{name} is missing a geometry column."
        )
    
    if not gdf.geometry.is_valid.all():
        raise ValueError(
            f"{name} contains empty geometries."
        )

    if not gdf.geometry.is_valid.all():
        raise ValueError(
            f"{name} contains invalid geometries"
        )

def _validate_districts_column(
        gdf: gpd.GeoDataFrame,
        district_col: str,
        name: str,
) -> None:
    """Validate that the district column exists"""
    if district_col not in gdf.columns:
        raise KeyError(
            f"{district_col!r} missing from {name}"
        )


def validate_districts(
        districts: gpd.GeoDataFrame,
        district_col: str,
) -> None:
    """Validate a district GeoDataFrame"""

    _validate_geodataframe(districts, "districts")
    _validate_geometry(districts, "districts")
    _validate_districts_column(districts, district_col, "districts")

def validate_building_data(
        buildings: gpd.GeoDataFrame,
        districts: gpd.GeoDataFrame,
        district_col: str,
) -> None:
    """Validate GeoDataFrames used for building indicator calculations"""

    validate_districts(districts, district_col)
    _validate_geodataframe(buildings, "buildings")
    _validate_geometry(buildings, "buildings")
    _validate_districts_column(buildings, district_col, "buildings")