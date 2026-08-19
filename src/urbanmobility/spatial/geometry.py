import geopandas as gpd
import pandas as pd

def points_gdf(
        trips_df: pd.DataFrame,
        lat_col: str,
        lon_col: str,
        source_crs: str = "EPSG:4326",
        target_crs: str = "EPSG:25833",
    ) -> gpd.GeoDataFrame:
    """
    Converts a DataFrame with coordinates to a GeoDataFrame with Shapely Point geometries.

    The function:
    1. Checks that the necessary coordinate columns exist.
    2. Creates Shapely Point geometries from the longitude/latitude columns.
    3. Sets the source CRS.
    4. Transforms the geometry to the target CRS.


    Parameters
    ----------
    trips_df : pd.DataFrame
        DataFrame that contains coordinate columns.
    lat_col: str
        Name of the column with latitude.
    lon_col: str
        Name of the column with longitude.
    source_crs : str, optional
        CRS of the input coordinates.
        Default is "EPSG:4326" (WGS84).
    target_crs: str, optional
        CRS to transform to after geometry creation.
        Default is "EPSG:25833".

    Returns
    -------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with point geometries and CRS set to "target_crs".
    
    Raises
    ------
    KeyError
        If either "lat_col" or "lon_col" does not exist in "trips_df".
    ValueError
        If the transformation to "target_crs" fails.

    """
    # Checks that both coordinate columns exist in trips_df
    if lat_col not in trips_df.columns or lon_col not in trips_df.columns:
        raise KeyError(f"{trips_df} is missing the columns {lat_col!r} and/or {lon_col!r}.")

    # Makes a GeoDataFrame based on trips_df
    gdf = gpd.GeoDataFrame(
        trips_df.copy(),
        geometry=gpd.points_from_xy(trips_df[lon_col], trips_df[lat_col]),
        crs=source_crs
    )

    # Transforms to target_crs
    try:
        return gdf.to_crs(target_crs)
    except Exception as e:
        raise ValueError(f"Could not transform CRS to {target_crs}: {e}")
