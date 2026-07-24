import geopandas as gpd


def validate_buildings_data(
        buildings: gpd.GeoDataFrame,
        districts: gpd.GeoDataFrame,
        district_col: str,
) -> None:


    for name, gdf in [
        ("buildings", buildings),
        ("districts", districts),
    ]:
        if not isinstance(gpd.GeoDataFrame):
            raise TypeError(
                f"{name} must be a GeoDataFrame"
            )

        if gdf.geometry.is_empty.any():
            raise ValueError(
                f"{name} contains empty geometries"
            )

        if gdf.crs is None:
            raise ValueError(
                f"{name} has no CRS"
            )

    if district_col not in buildings.columns:
        raise KeyError(
            f"{district_col!r} missing from buildings."
        )

    if district_col not in districts.columns:
        raise KeyError(
            f"{district_col!r} missing from districts."
        )