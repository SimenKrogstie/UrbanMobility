"""Check input assumptions"""

import geopandas as gpd


def validate_geodataframe(
    gdf: gpd.GeoDataFrame,
    name: str,
) -> None:
    """Validate basic GeoDataFrame assumptions."""

    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError(f"{name} must be a GeoDataFrame")

    if "geometry" not in gdf.columns:
        raise ValueError(f"{name} is missing a geometry column.")

    if gdf.geometry.is_empty.any():
        raise ValueError(f"{name} contains empty geometries.")

    if not gdf.geometry.is_valid.all():
        raise ValueError(f"{name} contains invalid geometries.")


def validate_column(
    gdf: gpd.GeoDataFrame,
    column: str,
    name: str,
) -> None:
    """Validate that a column exists."""

    if column not in gdf.columns:
        raise KeyError(f"{column!r} missing from {name}")


def validate_districts(
    districts: gpd.GeoDataFrame,
    district_col: str,
) -> None:
    """Validate district GeoDataFrame."""

    validate_geodataframe(
        districts,
        "districts",
    )

    validate_column(
        districts,
        district_col,
        "districts",
    )


def validate_building_data(
    buildings: gpd.GeoDataFrame,
    districts: gpd.GeoDataFrame,
    district_col: str,
) -> None:
    """Validate GeoDataFrames used for building analysis."""

    validate_geodataframe(
        buildings,
        "buildings",
    )

    validate_districts(
        districts,
        district_col,
    )

    validate_column(
        buildings,
        district_col,
        "buildings",
    )


def validate_indicators(
    gdf: gpd.GeoDataFrame,
    indicators: list[str],
) -> None:
    """Validate required indicator columns."""

    missing = [col for col in indicators if col not in gdf.columns]

    if missing:
        raise KeyError(f"Missing indicator columns: {missing}")


def _validate_districts_exist(
    gdf: gpd.GeoDataFrame,
    districts: list[str],
    district_col: str,
) -> None:
    """Validate requested districts exist."""

    missing = [d for d in districts if d not in gdf[district_col].unique()]

    if missing:
        raise KeyError(f"Districts not found: {missing}")


def validate_building_plot_data(
    buildings: gpd.GeoDataFrame,
    district_col: str,
    type_col: str,
) -> None:
    """Validate data required for building type plots."""

    validate_geodataframe(
        buildings,
        "buildings",
    )

    validate_column(
        buildings,
        district_col,
        "buildings",
    )

    validate_column(
        buildings,
        type_col,
        "buildings",
    )
