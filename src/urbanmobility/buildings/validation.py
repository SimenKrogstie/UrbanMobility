"""Check input assumptions"""

import geopandas as gpd

def validate_building_data(
        buildings: gpd.GeoDataFrame,
        districts: gpd.GeoDataFrame,
        district_col: str,
) -> None:
    
    for name, gdf in [
        ("buildings", buildings),
        ("districts", districts),
    ]:
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise TypeError(
                f"{name} must be a GeoDataFrame"
            )
        
        if gdf.crs is None:
            raise ValueError(
                f"{name} has no CRS"
            )
        
        if gdf.geometry.is_empty.any():
            raise ValueError(
                f"{name} contains empty geometries"
            )

        if not gdf.geometry.is_valid.all():
            raise ValueError(
                f"{name} contains invalid geometries"
            )

        for gdf, name in [
            (buildings, "buildings"),
            (districts, "districts")
        ]: 
            if district_col not in gdf.columns:
                raise KeyError(
                    f"{district_col!r} missing from {name}"
                )