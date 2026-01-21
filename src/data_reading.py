import geopandas as gpd
import pandas as pd
import pathlib
from helpers import CRS


def csv_to_df(
        path: str | pathlib.Path,
        sep: str = ",",
    ) -> pd.DataFrame:
    """
    Reads a CSV file and returns its content as a pandas DataFrame.

    The function:
    1. Verifies that the file exists.
    2. Reads the file with pandas using the specified separator.
    3. Wraps any reading errors in a clearer IOError.
    
    Parameters
    ----------
    path : str or pathlib.Path
        Path to the CSV file to be read. Can be a string or a 'pathlib.Path' object.
    sep : str, optional 
        Separator used in the CSV file.
        Default is ",".

    Returns
    -------
    df : pd.DataFrame
        DataFrame with the content of the CSV file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the specified path.
    IOError
        If the file cannot be read by pandas.
    """
    # Ensures that path is a Path() object
    path = pathlib.Path(path)

    # Checks that the file exists
    if not path.exists():
        raise FileNotFoundError(f"The file does not exist: {path}")

    # Tries to read the file with pandas
    try:
        df = pd.read_csv(path, sep=sep,)
    except Exception as e:
        raise IOError(f"Could not read the file '{path}': {e}")
    
    return df


def data_to_gdf(
        path: str | pathlib.Path,
        target_crs: str = "EPSG:25833"
    ) -> gpd.GeoDataFrame:
    """
    Reads a spatial data file into a GeoDataFrame and transforms it to the desired CRS.

    The function:
    1. Reads a geopandas-supported data file (GeoPackage, Shapefile, GeoJSON, etc.).
    2. Checks that the file exists before reading.
    3. Assumes "EPSG:4326" as the source CRS if the data lacks CRS information.
    4. Transforms to "target_crs" via the helper function "CRS()".

    Parameters
    -----------
    path : str or pathlib.Path
        Path to the spatial data file to be read.
    target_crs : str, optional
        CRS to transform to, in the form "EPSG:XXXX".
        Default is "EPSG:25833".

    Returns
    -------
    gdf : gpd.GeoDataFrame
        GeoDataFrame with geometry reprojected to "target_crs".

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the specified path.
    IOError
        If the file cannot be read by geopandas.
    ValueError
        If the CRS transformation fails, either due to an invalid CRS
        or an error in reprojection.
    """

    # Ensures that path is a Path() object
    path = pathlib.Path(path)

    # Checks that the file exists
    if not path.exists():
        raise FileNotFoundError(f"The file does not exist: {path}")

    # Tries to read the file with geopandas
    try:
        gdf = gpd.read_file(path)
    except Exception as e:
        raise IOError(f"Could not read the file '{path}': {e}")
    
    # Handles CRS with the helper function CRS()
    gdf = CRS(gdf, target_crs, name="data_to_gdf", wgs84_missing=True)
    
    return gdf