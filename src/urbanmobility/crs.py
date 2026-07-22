import geopandas as gpd
    
     
def CRS(
        gdf: gpd.GeoDataFrame,
        target_crs: str,
        *,
        name: str = "gdf",
        wgs84_missing: bool = False,
) -> gpd.GeoDataFrame:
    """
    Standardizes and ensures coordinate reference system (CRS) for a GeoDataFrame.

    The function:
    1. checks that a "geometry" column exists.
    2. Ensures "gdf.crs" is set (or sets it to EPSG:4326 if "wgs84_missing=True").
    3. Reprojects to "target_crs" if necessary.

    If "gdf" already has the same CRS as "target_crs", a copy is returned
    unchanged. Otherwise, the geometry is reprojected to "target_crs".

    Parameters
    ----------
    gdf : gdp.GeoDataFrame
        GeoDataFrame to be checked and potentially reprojected.
    target_crs : str
        Target CRS in the form "EPSG:XXXX" that the GeoDataFrame should have.
    name : str, optional
        Name used in error messages to make debugging easier.
        Default is "gdf".
    wgs84_missing : bool, optional
        If "True" and "gdf.crs" is missing, it is assumed that the data is in WGS84
        (EPSG:4326) and this CRS is set before any reprojecting.
        If "False" and "gdf.crs" is missing, ValueError is raised.
        Default is "False".

    Returns
    -------
    gdf : gpd.GeoDataFrame
        A copy of "gdf" where the CRS is equal to "target_crs".

    Raises
    ------
    ValueError:
        - "geometry"-column is missing.
        - CRS is missing and "wgs84_missing=False".
        - "target_crs" is not a string in the form "EPSG:XXXX".
        - reprojection fails.
    """
    
    gdf = gdf.copy()

    # Checks that the geometry column exists in gdf
    if "geometry" not in gdf.columns:
        raise ValueError(f"{name} is missing 'geometry'-column.")
    
    # Checks that target_crs is formatted as a string
    if not isinstance(target_crs, str) or not target_crs.strip().upper().startswith("EPSG:"):
        raise ValueError(
            f"{name}: target_crs must be a string, e.g. 'EPSG:XXXX'. "  
            f"Got {target_crs!r} ({type(target_crs).__name__})."
        )

    # Normalizes target_crs to uppercase and without spaces
    target_crs = target_crs.strip().upper()

    # Checks that CRS is set
    if gdf.crs is None:
        if wgs84_missing:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            raise ValueError(
                f"{name} is missing CRS. Set CRS before calling CRS(), "
                f"or use wgs84_missing=True."
            )

    # Makes current CRS a string for comparison
    current = str(gdf.crs).upper()

    # If CRS is already correct, return a copy without reprojection
    if current == target_crs:
        return gdf

    # Reprojects to 'target_crs'
    try:
        return gdf.to_crs(target_crs)
    except Exception as e:
        # Packages underlying error in a more readable ValueError
        raise ValueError(
            f"{name}: could not transform from {current} to {target_crs}: {e}"
        )