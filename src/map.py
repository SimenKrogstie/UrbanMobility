import geopandas as gpd
import folium
from helpers import CRS


def interaktivt_kart(
        mobilitet_gdf: gpd.GeoDataFrame,
        bygninger_gdf: gpd.GeoDataFrame,
        bydel_a: str,
        bydel_b: str,
        choropleth_col: str = "totalt_turer_per_km2",
        name_col: str = "bydel",
        popup_cols: list[str] | None = None,
        bygg_type_col: str = "building",
        bygg_bydel_col: str = "bydel",
) -> folium.Map:
    """
    Lager et interaktivt Folium-kart med mobilitetsindikatorer og bygninger
    for to utvalgte bydeler.

    Kartet inneholder:
    - Et choropleth-lag for de to bydelene, fargelagt etter en valgt
      mobilitetsindikator.
    - Popup med valgte kolonner (f.eks. bydelnavn og indikatorverdi).
    - Et bygninglag fargekodet etter bygningstype, filtrert til de samme
      bydelene.

    Parameters
    ----------
    mobilitet_gdf : gpd.GeoDataFrame
        GeoDataFrame med mobilitetsindikatorer.
    bygninger_gdf : gpd.GeoDataFrame
        GeoDataFrame med bygninger.
    bydel_a : str
        Navn på første bydel som skal vises.
    bydel_b : str
        Navn på andre bydel som skal vises.
    choropleth_col : str, optional
        Navnet på kolonnen i "mobilitet_gdf" som brukes til å fargelegge
        bydeler. 
        Default er "totalt_turer_per_km2".
    name_col : str, optional
        Kolonnenavn i "mobilitet_gdf" som inneholder bydelsnavn.
        Default er "bydel".
    popup_cols : list of str or None, optional
        Liste over kolonnenavn som skal vises i popup.
        Hvis "None" brukes "[name_col, choropleth_col]".
    bygg_type_col : str, optional
        Kolonnenavn for bygningstype i "bygninger_gdf".
        Default er "building".
    bygg_bydel_col : str, optional
        Kolonnenavn for bydel i "bygninger_gdf". Brukes til å filtrere
        bygninger til bydelene gitt av "bydel_a" og "bydel_b".
        Default er "bydel".

    Returns
    -------
    m : folium.Map
        Et Folium-kart-objekt med lag for mobilitetsindikatorer og bygninger.

    Raises
    ------
    KeyError
        Hvis nødvendige kolonner mangler i "mobilitet_gdf" eller
        "bygninger_gdf", eller hvis en av de oppgitte bydelene ikke finnes.
   	ValueError
        Hvis det ikke finnes bygninger i de valgte bydelene.
    """

    # Sikrer gyldig CRS
    gdf = CRS(mobilitet_gdf, target_crs="EPSG:4326", name="mobilitet_gdf", wgs84_mangler=True)

    # Resetter indeks hvis nødvendig
    if name_col not in gdf.columns and gdf.index.name == name_col:
        gdf = gdf.reset_index()

    # Sjekker at nødvendige kolonner finnes i mobilitet_gdf
    if name_col not in gdf.columns:
        raise KeyError(f"Kolonnen {name_col!r} finnes ikke i mobilitet_gdf.")
    if choropleth_col not in gdf.columns:
        raise KeyError(f"Kolonnen {choropleth_col!r} finnes ikke i mobilitet_gdf.")

    fokus = [bydel_a, bydel_b]

    # Sjekker at begge bydeler finnes i mobilitet_gdf
    for b in fokus:
        if b not in gdf[name_col].values:
            raise KeyError(f"Bydelen {b!r} finnes ikke i mobilitet_gdf[{name_col!r}].")

    # Default popup
    if popup_cols is None:
        popup_cols = [name_col, choropleth_col]

    # Oppretter kartet
    center = gdf.geometry.union_all().centroid
    m = folium.Map(
        location=[center.y, center.x],
        zoom_start=12,
        tiles="CartoDB positron",
        attr=(
            "© OpenStreetMap contributors (OSM) | "
            "Tiles © CARTO DB | "
            "Sykkelturer: © Oslo Bysykkel | "
            "Befolkningstall: © Oslo kommune / SSB"
        )
    )

    # Filtrerer til fokusbydeler
    fokus_mask = gdf[name_col].isin(fokus)
    gdf_fokus = gdf.loc[fokus_mask].copy()

    # Choropleth-lag for fokusbydeler
    folium.Choropleth(
        geo_data=gdf_fokus,
        data=gdf_fokus,
        columns=[name_col, choropleth_col],
        key_on=f"feature.properties.{name_col}",
        fill_color="YlGnBu",
        fill_opacity=0.9,
        line_opacity=0.3,
        highlight=False,
        name=f"{choropleth_col.replace('_', ' ')} (bydeler)",
    ).add_to(m)

    # GeoJson-lag for popups
    folium.GeoJson(
        gdf_fokus,
        style_function=lambda f: {
            "color": "black",
            "weight": 1,
            "fillOpacity": 0,
        },
        popup=folium.GeoJsonPopup(
            fields=popup_cols,
            aliases=[c.replace("_", " ") + ": " for c in popup_cols],
            localize=True,
            labels=True,
            sticky=False,
        ),
        control=False,
    ).add_to(m)

    # Sikrer gyldig CRS
    bygg = CRS(bygninger_gdf, target_crs="EPSG:4326", name="bygninger_gdf", wgs84_mangler=True,)

    # Sjekker at nødvendige kolonner finnes i bygninger_gdf
    if bygg_bydel_col not in bygg.columns:
        raise KeyError(f"Kolonnen {bygg_bydel_col!r} finnes ikke i bygninger_gdf.")
    if bygg_type_col not in bygg.columns:
        raise KeyError(f"Kolonnen {bygg_type_col!r} finnes ikke i bygninger_gdf.")

    # Filtrer bygninger til de valgte bydelene
    bygg = bygg[bygg[bygg_bydel_col].isin(fokus)].copy()

    if len(bygg) == 0:
        raise ValueError("Ingen bygninger finnes i de valgte bydelene.")

    # Håndterer manglende bygningstype
    bygg[bygg_type_col] = bygg[bygg_type_col].fillna("ukjent")
    typer = sorted(bygg[bygg_type_col].unique())

    # Fargemapping
    base_colors = [
        "#1b9e77", "#d95f02", "#7570b3", "#e7298a",
        "#66a61e", "#e6ab02", "#a6761d", "#666666",
        "#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6",
    ]
    type_to_color = {
        t: base_colors[i % len(base_colors)]
        for i, t in enumerate(typer)
    }

    # Leger eget lag for bygningstyper
    fg_bygg = folium.FeatureGroup(name="Bygningstyper", show=False)

    # Legger til hver bygning 
    for _, row in bygg.iterrows():
        btype = row[bygg_type_col]
        geom = row.geometry.__geo_interface__
        farge = type_to_color.get(btype, "#999999")

        folium.GeoJson(
            geom,
            style_function=lambda f, color=farge: {
                "fillColor": color,
                "color": color,
                "weight": 0.3,
                "fillOpacity": 0.6,
            },
            tooltip=folium.Tooltip(f"<b>Bygningstype:</b> {btype}"),
        ).add_to(fg_bygg)

    fg_bygg.add_to(m)

    
    folium.LayerControl(collapsed=False).add_to(m)
    return m