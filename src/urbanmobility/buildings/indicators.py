import geopandas as gpd
from ..spatial.crs import CRS

def building_indicators(
        buildings_gdf: gpd.GeoDataFrame,
        districts_gdf: gpd.GeoDataFrame,
        district_col: str = "bydel"
    ) -> gpd.GeoDataFrame:
    
    """
    Computes building-related indicators per district.

    The function:
    1. Ensures that district column exists in both "buildings_gdf" and "districts_gdf".
    2. Ensures common CRS for "buildings_gdf" and "districts_gdf".
    3. Calculates building area and aggregates count and total area per district.
    4. Merges this with "districts_gdf".
    5. Computes indicators for buildings.

    Parameters
    ----------
    buildings_gdf : gpd.GeoDataFrame
        GeoDataFrame with building polygons and district.
    districts_gdf : gpd.GeoDataFrame
        GeoDataFrame with district polygons and population data.
    district_col : str, optional
        Name of the column in "districts_gdf" containing district names.
        Default is "bydel".

    Returns
    -------
    building_indicators_gdf : gpd.GeoDataFrame
        GeoDataFrame indexed on "district_col" containing:
        - geometry
        - area in m^2 and km^2
        - number of buildings
        - total building area (m^2)
        - buildings per km^2
        - built-up area in percent
        - average building area (m^2)

    Raises
    ------
    KeyError
        If "bydel_col" is missing in "buildings_gdf" or "districts_gdf".
    ValueError
        If CRS is missing or CRS transformation fails.
    """
    buildings = buildings_gdf.copy()
    districts = districts_gdf.copy()

    # Checks that "district_col" exists in both GeoDataFrames
    if district_col not in buildings.columns:
        raise KeyError(f"{district_col!r} is missing in buildings_gdf.")
    if district_col not in districts.columns:
        raise KeyError(f"{district_col!r} is missing in districts_gdf.")

    # Ensures proper CRS in both GeoDataFrames
    target_crs = "EPSG:25833"
    districts = CRS(districts, target_crs, name="districts_gdf")
    buildings = CRS(buildings, target_crs, name="buildings_gdf") 
    
    # Computes building area
    buildings["area_m2"] = buildings.geometry.area

    # Aggregates building data per district
    agg = (
        buildings.groupby(district_col)
        .agg(
            num_buildings=("geometry", "size"),
            building_area_m2=("area_m2", "sum")
        )
        .reset_index()
    )

    # Merges aggregated values with districts
    districts = districts.merge(agg, on=district_col, how="left")

    # Districts without buildings get 0 in the indicators
    districts[["num_buildings", "building_area_m2"]] = (districts[["num_buildings", "building_area_m2"]].fillna(0))

    # Computes district area in m^2 and km^2
    districts["area_m2"] = districts.geometry.area
    districts["area_km2"] = districts.geometry.area / 1000000

    # Computes building indicators
    districts["buildings_per_km2"] = districts["num_buildings"] / districts["area_km2"]
    districts["built_up_area_percent"] = (districts["building_area_m2"] / districts["area_m2"]) * 100
    
    # Computes average building size
    mask = districts["num_buildings"] > 0
    districts["avg_building_area_m2"] = 0.0
    districts.loc[mask, "avg_building_area_m2"] = districts.loc[mask, "building_area_m2"] / districts.loc[mask, "num_buildings"]

    # Sets district as index
    building_indicators_gdf = districts.set_index(district_col)

    return building_indicators_gdf