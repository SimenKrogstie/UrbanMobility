import geopandas as gpd
import pandas as pd
import pathlib
from helpers import CRS


def csv_til_df(
        path: str | pathlib.Path,
        sep: str = ",",
    ) -> pd.DataFrame:
    """
    Leser en CSV-fil og returnerer innholdet som en pandas DataFrame.

    Funksjonen gjør følgende:
    1. Verifiserer at at filen eksisterer.
    2. Leser filen med pandas og angitt separator.
    3. Pakker eventuelle lesefeil i en tydligere IOError. 
    
    Parameters
    ----------
    path : str or pathlib.Path
        Filsti til csv-filen som skal leses. Kan være streng og 'pathlib.Path'-objekt.
    sep : str, optional 
        Kolonneseparator. Default er ",".

    Returns
    -------
    df : pd.DataFrame
        DataFrame med innholdet fra CSV-filen.

    Raises
    ------
    FileNotFoundError
        Hvis filen ikke finnes på oppgitt sti.
    IOError
        Hvis filen ikke kan leses av pandas.
    """
    # Sørger for at path er et Path()-objekt
    path = pathlib.Path(path)

    # Sjekker at filen eksisterer
    if not path.exists():
        raise FileNotFoundError(f"Filen finnes ikke: {path}")
    
    # Forsøker å lese filen med pandas
    try:
        df = pd.read_csv(path, sep=sep,)
    except Exception as e:
        raise IOError(f"Kunne ikke lese filen '{path}': {e}")
    
    return df


def data_til_gdf(
        path: str | pathlib.Path,
        target_crs: str = "EPSG:25833"
    ) -> gpd.GeoDataFrame:
    """
    Leser en romlig datafil til en GeoDataFrame og transformerer til ønsket CRS.

    Funksjonen:
    1. Leser en geopandas-støtte datafil (GeoPackage, Shapefile, GeoJSON, osv.).
    2. Sjekker at filen eksisterer før innleseing.
    3. Antar "EPSG:4326" som kilde-CRS dersom dataene mangler CRS.
    4. Transformerer til "target_crs" via hjelpefunksjonen "CRS()".


    Parameters
    -----------
    path : str or pathlib.Path
        Sti til datafil som skal leses.
    target_crs : str, optional
        CRS det skal transformeres til, på formen "EPSG:XXXX".
        Default er "EPSG:25833".
    
    Returns
    -------
    gdf : gpd.GeoDataFrame
        GeoDataFrame med geometri reprojisert til "target_crs".

    Raises
    ------
    FileNotFoundError
        Hvis filen ikke finnes på angitt sted.
    IOError
        Hvis filen ikke kan leses av geopandas.
    ValueError
        Hvis CRS-transformasjonen feiler, enten på grunn av ugyldig CRS
        eller feil i reprojeksjon.
    """
    # Sørger for at path er et Path()-objekt
    path = pathlib.Path(path)
    
    # Sjekker at filen eksisterer
    if not path.exists():
        raise FileNotFoundError(f"Filen finnes ikke: {path}")
    
    # Forsøker å lese filen med geopandas
    try:
        gdf = gpd.read_file(path)
    except Exception as e:
        raise IOError(f"Kunne ikke lese filen '{path}': {e}")
    
    # Håndterer CRS med hjelpefunksjonen CRS()
    gdf = CRS(gdf, target_crs, name="data_til_gdf", wgs84_mangler=True)
    
    return gdf