import geopandas as gpd
import pandas as pd
from src.helpers import CRS


def mobilityindicators(
        districts_gdf: gpd.GeoDataFrame,
        trips_df: pd.DataFrame,
        population_col: str = "befolkning_2024",
        district_col: str = "bydel",
        start_col: str = "start_district",
        end_col: str = "end_district"
    ) -> gpd.GeoDataFrame:
    """
    Computes mobility and area-based indicators for each district.
    
    The function:
    1. Ensures valid CRS and geometry in "districts_gdf".
    2. Calculates area and population density for each district.
    3. Counts number of trip start and end points per district.
    4. Combines results into a GeoDataFrame with indicators per district.

    Parameters
    ----------
    districts_gdf : gpd.GeoDataFrame
        GeoDataFrame with districtpolygons and population data.
    trips_df : pd.DataFrame
        DataFrame with trip data and start and end districts.
    population_col : str, optional
        Name of the column in "districts_gdf" containing population numbers.
        Default is "befolkning_2024"
    district_col : str, optional
        Name of the column in "districts_gdf" containing district names.
        Default is "bydel".
    start_col : str, optional
        Name of the column in "trips_df" for start district.
        Default is "start_district".
    end_col : str, optional
        Name of the column in "trips_df" for end district.
        Default is "end_district".

    Returns
    -------
    mobilitet : gpd.GeoDataFrame
        GeoDataFrame indexed on "district_col" containing:
        - geometry
        - area (km^2)
        - population and population density
        - trips started / ended
        - trips per km^2 and per capita
        - net and total number of trips
    
    Raises
    ------
    KeyError
        If required columns are missing in "districts_gdf" or "trips_df".
    ValueError
        If "districts_gdf" lacks CRS or CRS transformation fails.
    """

    # Ensures valid geometry and CRS
    districts_gdf = CRS(districts_gdf, str(districts_gdf.crs), name="districts_gdf")

    # Beregner areal i km^2 og befolkningstetthet
    districts = districts_gdf.copy()
    districts["area_km2"] = districts.geometry.area / 1000000
    districts["population_density_km2"] = districts[population_col] / districts["area_km2"]

    # Counts trips started and ended per district
    start_per_district = (
        trips_df.groupby(start_col)
        .size()
        .rename("trips_started")
    )

    end_per_district = (
        trips_df.groupby(end_col)
        .size()
        .rename("trips_ended")
    )

    # Combining district and trip data
    mobility = (
        districts.set_index(district_col)[["geometry", "area_km2", population_col, "population_density_km2"]]
        .join([start_per_district, end_per_district])
        .fillna(0)
    )

    # Computes net and total number of trips
    mobility["net_trips"] = mobility["trips_ended"] - mobility["trips_started"]
    mobility["total_trips"] = mobility["trips_started"] + mobility["trips_ended"]

    # Computes area-based indicators
    mobility["trips_started_per_km2"] =  mobility["trips_started"] / mobility["area_km2"]
    mobility["trips_ended_per_km2"] = mobility["trips_ended"] / mobility["area_km2"]
    mobility["net_trips_per_km2"] = mobility["net_trips"] / mobility["area_km2"]
    mobility["total_trips_per_km2"] = mobility["total_trips"] / mobility["area_km2"]

    # Computes population-based indicators
    mobility["trips_started_per_capita"] = mobility["trips_started"] / mobility[population_col]
    mobility["trips_ended_per_capita"] = mobility["trips_ended"] / mobility[population_col]
    mobility["net_trips_per_capita"] = mobility["net_trips"] / mobility[population_col]
    mobility["total_trips_per_capita"] = mobility["total_trips"] / mobility[population_col]

    return mobility


def buildingindicators(
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
    buildingsindicators_gdf : gpd.GeoDataFrame
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
            antall_bygninger=("geometry", "size"),
            bygning_areal_m2=("area_m2", "sum")
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
    buildingsindicators_gdf = districts.set_index(district_col)

    return buildingsindicators_gdf