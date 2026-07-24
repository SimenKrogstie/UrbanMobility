import geopandas as gpd

def add_building_metrics(
        districts: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:

    districts = districts.copy()

    districts["area_m2"] = districts.geometry.area
    districts["area_km2"] = districts["area_m2"] / 1_000_000

    districts["buildings_per_km2"] = (
        districts["num_buildings"]
        / districts["area_km2"]
    )

    districts["built_up_area_percent"] = (
        districts["building_area_m2"]
        / districts["area_m2"]
        * 100
    )

    districts["avg_building_area_m2"] = (
        districts["building_area_m2"]
        .div(districts["building_area_m2"]
        .fillna(0))
    )

    return districts