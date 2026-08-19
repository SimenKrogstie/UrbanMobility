import geopandas as gpd


def CRS(
    gdf: gpd.GeoDataFrame,
    target_crs: str,
    *,
    name: str = "gdf",
    wgs84_missing: bool = False,
) -> gpd.GeoDataFrame:
    """Checks CRS of GeoDataFrame"""

    gdf = gdf.copy()

    if gdf.crs is None:
        if wgs84_missing:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            raise ValueError(f"{name} has no CRS.")

    if str(gdf.crs).upper() == target_crs.upper():
        return gdf

    try:
        return gdf.to_crs(target_crs)
    except Exception as e:
        raise ValueError(f"{name}: failed to convert CRS to {target_crs}: {e}") from e
