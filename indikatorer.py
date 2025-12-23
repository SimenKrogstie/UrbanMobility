import geopandas as gpd
import pandas as pd
from helpers import CRS


def mobilitetsindikatorer(
        bydeler_gdf: gpd.GeoDataFrame,
        turer_df: pd.DataFrame,
        befolkning_col: str = "befolkning_2024",
        bydel_col: str = "bydel",
        start_col: str = "start_bydel",
        slutt_col: str = "slutt_bydel"
    ) -> gpd.GeoDataFrame:
    """
    Beregner mobilitets- og arealbaserte indikatorer for hver bydel.

    Funksjonen:
    1. Sikrer gyldig CRS og geometri i "bydeler_gdf".
    2. Beregner areal og befolkningstetthet for hver bydel.
    3. Teller antall start- og sluttpunkter per bydel.
    4. Kombinerer resultater til en GeoDataFrame med indikatorer per bydel.

    Parameters
    ----------
    bydeler_gdf : gpd.GeoDataFrame
        GeoDataFrame med bydelspolygoner og befolkningsdata.
    turer_df : pd.DataFrame
        DataFrame med turdata og start- og sluttbydel.
    befolkning_col : str, optional
        Navn på kolonnen i "bydeler_gdf" som inneholder befolkningstall.
        Default er "befolkning_2024"
    bydel_col : str, optional
        Navn på kolonnen i "bydeler_gdf" som inneholder bydelnavn.
        Default er "bydel".
    start_col : str, optional
        Navn på kolonnen i "turer_df" for startbydel.
        Default er "start_bydel".
    slutt_col : str, optional
        Navn på kolonnen i "turer_df" for sluttbydel.
        Default er "slutt_bydel".

    Returns
    -------
    mobilitet : gpd.GeoDataFrame
        GeoDataFrame indeksert på "bydel_col" som inneholder:
        - geometri
        - areal (km^2)
        - befolkning og befolkningstetthet
        - turer startet /sluttet
        - turer per km^2 og per innbygger
        - netto og totalt antall turer
    
    Raises
    ------
    KeyError
        Hvis nødvendige kolonner mangler i "bydeler_gdf" eller "turer_df".
    ValueError
        Hvis "bydeler_gdf" mangler CRS eller CRS-transformasjonen feiler.
    """

    # Sikrer at geometri og CRS er gyldige 
    bydeler_gdf = CRS(bydeler_gdf, str(bydeler_gdf.crs), name="bydeler_gdf")

    # Beregner areal i km^2 og befolkningstetthet
    bydeler = bydeler_gdf.copy()
    bydeler["areal_km2"] = bydeler.geometry.area / 1000000
    bydeler["befolkningstetthet_km2"] = bydeler[befolkning_col] / bydeler["areal_km2"]

    # Teller turer per bydel (start og slutt)
    start_per_bydel = (
        turer_df.groupby(start_col)
        .size()
        .rename("turer_startet")
    )

    slutt_per_bydel = (
        turer_df.groupby(slutt_col)
        .size()
        .rename("turer_sluttet")
    )

    # Kombinerer bydel- og turdata
    mobilitet = (
        bydeler.set_index(bydel_col)[["geometry", "areal_km2", befolkning_col, "befolkningstetthet_km2"]]
        .join([start_per_bydel, slutt_per_bydel])
        .fillna(0)
    )

    # Beregner netto og totalt antall turer
    mobilitet["netto_turer"] = mobilitet["turer_sluttet"] - mobilitet["turer_startet"]
    mobilitet["turer_totalt"] = mobilitet["turer_startet"] + mobilitet["turer_sluttet"]

    # Beregner arealbaserte indikatorer
    mobilitet["turer_startet_per_km2"] =  mobilitet["turer_startet"] / mobilitet["areal_km2"]
    mobilitet["turer_sluttet_per_km2"] = mobilitet["turer_sluttet"] / mobilitet["areal_km2"]
    mobilitet["netto_turer_per_km2"] = mobilitet["netto_turer"] / mobilitet["areal_km2"]
    mobilitet["totalt_turer_per_km2"] = mobilitet["turer_totalt"] / mobilitet["areal_km2"]

    # Beregner befolknignsbaserte indikatorer
    mobilitet["turer_startet_per_innbygger"] = mobilitet["turer_startet"] / mobilitet[befolkning_col]
    mobilitet["turer_sluttet_per_innbygger"] = mobilitet["turer_sluttet"] / mobilitet[befolkning_col]
    mobilitet["netto_turer_per_innbygger"] = mobilitet["netto_turer"] / mobilitet[befolkning_col]
    mobilitet["totalt_turer_per_innbygger"] = mobilitet["turer_totalt"] / mobilitet[befolkning_col]

    return mobilitet


def bygningsindikatorer(
        bygninger_gdf: gpd.GeoDataFrame,
        bydeler_gdf: gpd.GeoDataFrame,
        bydel_col: str = "bydel"
    ) -> gpd.GeoDataFrame:
    
    """
    Beregner bygningsrelatert indikatorer per bydel.

    Funksjonen:
    1. Sikrer at bydelkolonne finnes i både "bygninger_gdf" og "bydeler_gdf".
    2. Sikrer felles CRS for "bygninger_gdf" og "bydeler_gdf".
    3. Beregner bygnignsareal og aggregerer antall og totalt areal per bydel.
    4. Slår dette sammen med "bydeler_gdf".
    5. Beregner indikatorer for bygninger. 

    Parameters
    ----------
    bygninger_gdf : gpd.GeoDataFrame
        GeoDataFrame med bygnignspolygon og bydel.
    bydeler_gdf : gpd.GeoDataFrame
        GeoDataFrame med bydelspolygoner og befolkningsdata.
    bydel_col : str, optional
        Navn på kolonnen i "bydeler_gdf" som inneholder bydelnavn.
        Default er "bydel".

    Returns
    -------
    bygningsindikatorer_gdf : gpd.GeoDataFrame
        GeoDataFrame indeksert på "bydel_col" som inneholder:
        - geometri
        - areal i m^2 og km^2
        - antall bygninger
        - totalt bygningsareal (m^2)
        - bygninger per km^2
        - bebygd areal i prosent
        - gjennomsnittlig bygningsarel (m^2)

    Raises
    ------
    KeyError
        Hvis "bydel_col" mangler i "bygninger_gdf" eller "bydeler_gdf".
    ValueError
        Hvis CRS mangler eller CRS-transformasjonen feiler.
    """
    bygg = bygninger_gdf.copy()
    bydeler = bydeler_gdf.copy()

    # Sjekker at "bydel_col" finnes i "bygnigner_gdf" og "bydeler_gdf"
    if bydel_col not in bygg.columns:
        raise KeyError(f"{bydel_col!r} mangler i bygninger_gdf.")
    if bydel_col not in bydeler.columns:
        raise KeyError(f"{bydel_col!r} mangler i bydeler_gdf.")
    
    # Sikrer felels og metrisk CRS i begge gdf
    target_crs = "EPSG:25833"
    bydeler = CRS(bydeler, target_crs, name="bydeler_gdf")
    bygg = CRS(bygg, target_crs, name="bygninger_gdf") 
    
    # Beregner bygnignsareal
    bygg["areal_m2"] = bygg.geometry.area

    # Aggrergerer bygningsdata per bydel
    agg = (
        bygg.groupby(bydel_col)
        .agg(
            antall_bygninger=("geometry", "size"),
            bygning_areal_m2=("areal_m2", "sum")
        )
        .reset_index()
    )

    # Slår aggregerte verdier sammen med bydeler
    bydeler = bydeler.merge(agg, on=bydel_col, how="left")

    # Bydeler uten bygninger får 0 i indikatorene
    bydeler[["antall_bygninger", "bygning_areal_m2"]] = (bydeler[["antall_bygninger", "bygning_areal_m2"]].fillna(0))

    # Beregner bydelsareal i m^2 og km^2
    bydeler["areal_m2"] = bydeler.geometry.area
    bydeler["areal_km2"] = bydeler.geometry.area / 1000000

    # Beregner bygningsindikatorer
    bydeler["bygninger_per_km2"] = bydeler["antall_bygninger"] / bydeler["areal_km2"]
    bydeler["bebygd_areal_prosent"] = (bydeler["bygning_areal_m2"] / bydeler["areal_m2"]) * 100

    # Beregner gjennomsnittlig bygningsstørrelse
    mask = bydeler["antall_bygninger"] > 0
    bydeler["avg_bygning_areal_m2"] = 0.0
    bydeler.loc[mask, "avg_bygning_areal_m2"] = bydeler.loc[mask, "bygning_areal_m2"] / bydeler.loc[mask, "antall_bygninger"]
    
    # Setter bydel som indeks
    bygningsindikatorer_gdf = bydeler.set_index(bydel_col)
    
    return bygningsindikatorer_gdf