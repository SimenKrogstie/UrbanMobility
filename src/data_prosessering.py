import geopandas as gpd
import pandas as pd
import osmnx as ox
from helpers import CRS


def punkter_gdf(
        turer_df: pd.DataFrame,
        lat_col: str,
        lon_col: str,
        source_crs: str = "EPSG:4326",
        target_crs: str = "EPSG:25833",
    ) -> gpd.GeoDataFrame:
    """
    Konverterer en DataFrame med koordinater til en GeoDataFrame med Shapely Point-geometrier.

    Funksjonen:
    1. Sjekker at nødvendige koordinatkolonner finnes.
    2. Oppretter Shapely Point-geometrier fra longtitude/latitude-kolonnene.
    3. Setter kilde-CRS ("source_crs").
    4. Transformerer geometrien til "target_crs".


    Parameters
    ----------
    turer_df : pd.DataFrame
        DataFrame som inneholder koordinatkolonner.
    lat_col: str
        Navn på kolonne med breddegrad (latitude).
    lon_col: str
        Navn på kolonne med lengdegrad (longitude).
    source_crs : str, optional
        CRS for de opprinnelige koordinatene.
        Default er "EPSG:4326" (WGS84).
    target_crs: str, optional
        CRS det skal transformeres til etter geometrioppretting.
        Default er "EPSG:25833".

    Returns
    -------
    gdf : gpd.GeoDataFrame
        GeoDataFrame med punktgeometrier og CRS satt til "target_crs".
    
    Raises
    ------
    KeyError
        Hvis enten "lat_col" eller "lon_col" ikke finnes i "turer_df".
    ValueError
        Hvis reprojeksjonen til "target_crs" mislykkes.

    """
    # Sjekker at begge koordinatkolonner eksisterer i turer_df
    if lat_col not in turer_df.columns or lon_col not in turer_df.columns:
        raise KeyError(f"{turer_df} mangler kolonnene {lat_col!r} og/eller {lon_col!r}.")

    # Lager en GeoDataFrame basert på turer_df
    gdf = gpd.GeoDataFrame(
        turer_df.copy(),
        geometry=gpd.points_from_xy(turer_df[lon_col], turer_df[lat_col]),
        crs=source_crs
    )

    # Forsøker å transformere CRS til target_crs
    try:
        return gdf.to_crs(target_crs)
    except Exception as e:
        raise ValueError(f"Kunne ikke transformere CRS til {target_crs}: {e}")


def legg_til_bydeler(
        turer_df: pd.DataFrame,
        start_gdf: gpd.GeoDataFrame,
        slutt_gdf: gpd.GeoDataFrame,
        bydeler_gdf: gpd.GeoDataFrame,
        bydel_col: str = "bydel",
    ) -> pd.DataFrame:
    """
    Legger til kolonner med bydelnavn for start- og sluttpunkter basert på spatial join.

    Funksjonen:
    1. Verifiserer at bydelgeometrien har CRS og at bydelkolonnen finnes. 
    2. Reprojiserer start- og sluttpunkter til samme CRS som bydelpolygonene.
    3. Utfører spatial join for begge punktsett. 
    4. Returnerer en DataFrame med to nye kolonner: "start_bydel" og "slutt_bydel".

    Parameters
    ----------
    turer_df : pd.DataFrame
        Den opprinnelige DataFrame-en med turdata (uten geometri).
    start_gdf : gpd.GeoDataFrame
        GeoDataFrame med punktgeometrier for startposisjonene.
    slutt_gdf : gpd.GeoDataFrame
        GeoDataFrame med punktgeometrier for sluttposisjonene.
    bydeler_gdf : gpd.GeoDataFrame
        GeoDataFrame med shapely Polygon/Multipolygon-geometrier for bydeler.
    bydel_col : str, optional
        Navnet på kolonnen i "bydeler_gdf" som inneholder bydelnavn.
        Default er "bydel".
   
    Returns
    -------
    turer : pd.DataFrame
        En kopi av "turer_df" med to nye kolonner: "start_bydel" og "slutt_bydel".

    Raises
    ------
    KeyError
        Hvis "bydel_col" ikke finnes i "bydeler_gdf".
    ValueError
        Hvis "bydeler_gdf" mangler CRS eller CRS-transformasjonen feiler.
    """
    # Sjekker at kolonnen med bydelnavn finnes i bydeler_gdf
    if bydel_col not in bydeler_gdf.columns:
        raise KeyError(f"bydeler_gdf mangler kolonnen {bydel_col!r}.")
    
    # Sjekker at bydeler har gyldig CRS
    bydeler_gdf = CRS(bydeler_gdf, str(bydeler_gdf.crs), name="bydeler_gdf")

    # Reprojiserer start- og sluttpunkter til samme CRS som bydeler.
    start_gdf = CRS(start_gdf, str(bydeler_gdf.crs), name="start_gdf")
    slutt_gdf = CRS(slutt_gdf, str(bydeler_gdf.crs), name="slutt_gdf")

    # Spatial join for startpunkter
    start_join = gpd.sjoin(
        start_gdf,
        bydeler_gdf[[bydel_col, "geometry"]],
        how="left",
        predicate="within"
    ).rename(columns={bydel_col: "start_bydel"})

    # Spatial join for sluttpunkter
    slutt_join = gpd.sjoin(
        slutt_gdf,
        bydeler_gdf[[bydel_col, "geometry"]],
        how="left",
        predicate="within"
    ).rename(columns={bydel_col: "slutt_bydel"})

    # Legger til de nye kolonnene i turer_df.
    turer = turer_df.copy()
    turer["start_bydel"] = start_join["start_bydel"].values
    turer["slutt_bydel"] = slutt_join["slutt_bydel"].values

    return turer


def hent_bygninger(
    bydeler_gdf: gpd.GeoDataFrame,
    bydel_col: str = "bydel",
    query: str = "Oslo, Norway",
    tags: dict | None = None,
) -> gpd.GeoDataFrame:
    """
    Henter bygninger fra OpenStreetMap (OSM) og knytter dem til bydeler via spatial join.

    Funksjonen:
    1. Validerer at "bydeler_gdf" har nødvendig CRS og kolonner.
    2. Sikrer at "bydeler_gdf" har gyldig CRS og reprojiserer til "EPSG:25833".
    3. Henter bygninger fra OSM basert på query og tags.
    4. Filtrerer ut kun Polygon/MultiPolygon-geometrier.
    5. Reprojiserer bygninger til samme CRS som "bydeler_gdf".
    6. Utfører spatial join for å finne hvilken bydel hver bygning tilhører.

    Parameters
    ----------
    bydeler_gdf : gpd.GeoDataFrame
        GeoDataFrame med shapely Polygon/Multipolygon-geometrier for bydeler.
    bydel_col : str, optional
        Navnet på kolonnen i "bydeler_gdf" som inneholder bydelnavn.
        Default er "bydel".
    query : str, optional
        Stedsnavn brukt av OSM for å hente bygninger.
        Default er "Oslo, Norway".
    tags : dict or None, optional
        OSM-tags-filtre.
        Default er "{"building": True}".

    Returns
    -------
    bygninger_i_bydeler : gpd.GeoDataFrame
        GeoDataFrame med bygnigner fra OSM reprojijsert til "EPSG:25833".
        Inneholder geometri for bygningene og bydelnavn.
    
    Raises
    ------
    KeyError
        Hvis "bydel_col" ikke finnes i "bydeler_gdf".
    ValueError
        Hvis "bydeler_gdf" mangler CRS eller CRS-transformasjonen feiler.
    """
    target_crs = "EPSG:25833"
    
    # Henter alle typer bygg fra OpenStreetMap.
    if tags is None:
        tags = {"building": True}

    # Sjekker at kolonnen med bydelnavn finnes i bydeler_gdf
    if bydel_col not in bydeler_gdf.columns:
        raise KeyError(f"Kolonnen {bydel_col!r} finnes ikke i bydeler_gdf.")
    if "geometry" not in bydeler_gdf.columns:
        raise ValueError("bydeler_gdf mangler 'geometry'-kolonne.")

    # Sikrer at bydeler har gyldig CRS og reprojiserer til target_crs.
    bydeler_gdf = CRS(bydeler_gdf, target_crs, name="bydeler_gdf")

    # Henter bygninger fra OSM 
    bygninger = ox.features_from_place(query=query, tags=tags)

    # Beholder kun Polygon/MultiPolygon-geometrier
    bygninger = bygninger[
        bygninger.geometry.type.isin(["Polygon", "MultiPolygon"])
    ].copy()

    # Reprojiserer bygnigner til target_crs
    bygninger = CRS(bygninger, target_crs ,name="bygninger", wgs84_mangler=True)

    # Filtrerer kolonner som trengs til spatial join
    bydel_join = bydeler_gdf[[bydel_col, "geometry"]]

    # Finner bydelen bygningene ligger innenfor med spatial join
    bygninger_i_bydel = gpd.sjoin(
        bygninger,
        bydel_join,
        how="left",
        predicate="within",
    ).drop(columns=["index_right"])

    return bygninger_i_bydel