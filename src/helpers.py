import geopandas as gpd
    
     
def CRS(
        gdf: gpd.GeoDataFrame,
        target_crs: str,
        *,
        name: str = "gdf",
        wgs84_mangler: bool = False,
) -> gpd.GeoDataFrame:
    """
    Standardiserer og sikrer koordinatsystem (CRS) for en GeoDataFrame.

    Funksjonen gjør tre hovedting:
    1. sjekker at det finnes en "geometry"-kolonne.
    2. Sikrer at "gdf.crs" er satt (eller setter den til EPSG:4326 hvis
        "wgs84_mangler=True").
    3. Reprojiserer til "target_crs" dersom nødvendig.

    Dersom "gdf" allerede har samme CRS som "target_crs" returneres en kopi
    uendret. Eller reprojiseres geometrien til "target_crs".

    Parameters
    ----------
    gdf : gdp.GeoDataFrame
        GeoDataFrame som skal kontrolleres og eventuelt reprojiseres.
    target_crs : str
        Mål-CRS på formen "EPSG:XXXX" som GeoDataFrame skal ha.
    name : str, optional
        Navn brukt i feilmeldinger for å gjøre feilsøkinger enklere.
        Default er "gdf".
    wgs84_mangler : bool, optional
        Hvis "True" og "gdf.crs" mangler, antas at dataene er i WGS84
        (EPSG:4326) og dette CRS settes før eventuell reprojeksjon.
        Hvis "False" og "gdf.crs" mangler, ValueError.
        Default er "False".

    Returns
    -------
    gdf : gpd.GeoDataFram"
        En kopi av "gdf" der CRS er lik "target_crs".

    Raises
    ------
    ValueError hvis:
        - "geometry"-kolonnen mangler.
        - CRS mangler og "wgs84_mangler=False".
        - "target_crs" ikke er en streng på formen "EPSG:XXXX".
        - reprojeksjon feiler.
    """
    
    gdf = gdf.copy()

    # Sjekker at geometri-kolonnen finnes i gdf
    if "geometry" not in gdf.columns:
        raise ValueError(f"{name} mangler 'geometry'-kolonne.")
    
    # Sjekker at target_crs er formatert som en streng
    if not isinstance(target_crs, str) or not target_crs.strip().upper().startswith("EPSG:"):
        raise ValueError(
            f"{name}: target_crs må være en streng, e.g. 'EPSG:XXXX'. "  
            f"Fikk {target_crs!r} ({type(target_crs).__name__})."
        )
    
    # Normaliserer target_crs til store bokstaver og uten mellomrom
    target_crs = target_crs.strip().upper()

    # Sjekker at CRS er satt
    if gdf.crs is None:
        if wgs84_mangler:
            gdf = gdf.set_crs("EPSG:4326")
        else:
            raise ValueError(
                f"{name} mangler CRS. Sett CRS før du kaller CRS(), "
                f"eller bruk wgs84_mangler=True."
            )
    
    # Gjør nåværende CRS til streng for å sammenligen
    current = str(gdf.crs).upper()

    # Hvis CRS allerede er riktig returneres en kopi uten reprojeksjon
    if current == target_crs:
        return gdf
    
    # Reprojiserer til 'target_crs'
    try:
        return gdf.to_crs(target_crs)
    except Exception as e:
        # Pakker underliggende feil i en mer lesbar ValueError
        raise ValueError(
            f"{name}: kunne ikke transformere fra {current} til {target_crs}: {e}"
        )