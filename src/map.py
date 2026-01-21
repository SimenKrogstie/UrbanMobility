import geopandas as gpd
import folium
from src.helpers import CRS


def interactive_map(
        mobility_gdf: gpd.GeoDataFrame,
        buildings_gdf: gpd.GeoDataFrame,
        district_a: str,
        district_b: str,
        choropleth_col: str = "total_trips_per_km2",
        name_col: str = "bydel",
        popup_cols: list[str] | None = None,
        building_type_col: str = "building",
        building_district_col: str = "bydel",
) -> folium.Map:
    """
    Makes an interactive Folium map with mobility indicators and buildings
    for two selected districts.

    The map contains:
    - A choropleth layer for the two districts, colored by a selected
      mobility indicator.
    - Popup with selected columns (e.g., district name and indicator value).
    - A building layer colored by building type, filtered to the same
      districts.    

    Parameters
    ----------
    mobility_gdf : gpd.GeoDataFrame
        GeoDataFrame with mobility indicators.
    buildings_gdf : gpd.GeoDataFrame
        GeoDataFrame with buildings.
    district_a : str
        Name of the first district to be displayed.
    district_b : str
        Name of the second district to be displayed.
    choropleth_col : str, optional
        Name of the column in "mobility_gdf" used to color the districts.
        Default is "total_trips_per_km2".
    name_col : str, optional
        Name of the column in "mobility_gdf" containing district names.
        Default is "bydel".
    popup_cols : list of str or None, optional
        List of column names to be displayed in the popup.
        If "None", [name_col, choropleth_col]" is used.
    building_type_col : str, optional
        Name of the column in "buildings_gdf" containing building types.
        Default is "building".
    building_district_col : str, optional
        Name of the column in "buildings_gdf" containing district names.
        Used to filter buildings to the districts specified by "district_a" and "district_b".
        Default is "bydel".
    
    Returns
    -------
    m : folium.Map
        A Folium map object with layers for mobility indicators and buildings.

    Raises
    ------
    KeyError
        If necessary columns are missing in "mobility_gdf" or
        "buildings_gdf", or if one of the specified districts does not exist.
    ValueError
        If there are no buildings in the selected districts.
    """

    # Ensures valid CRS
    gdf = CRS(mobility_gdf, target_crs="EPSG:4326", name="mobility_gdf", wgs84_missing=True)

    # Resets index if needed
    if name_col not in gdf.columns and gdf.index.name == name_col:
        gdf = gdf.reset_index()

    # Checks that necessary columns exist in mobility_gdf
    if name_col not in gdf.columns:
        raise KeyError(f"Column {name_col!r} does not exist in mobility_gdf.")
    if choropleth_col not in gdf.columns:
        raise KeyError(f"Column {choropleth_col!r} does not exist in mobility_gdf.")

    # Checks that both districts exist in mobility_gdf
    focus = [district_a, district_b]
    for b in focus:
        if b not in gdf[name_col].values:
            raise KeyError(f"District {b!r} does not exist in mobility_gdf[{name_col!r}].")
        
    # Default popup
    if popup_cols is None:
        popup_cols = [name_col, choropleth_col]

    # Creates the map
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

    # Filter to focus districts
    focus_mask = gdf[name_col].isin(focus)
    gdf_focus = gdf.loc[focus_mask].copy()

    # Choropleth-lag for focus districts
    folium.Choropleth(
        geo_data=gdf_focus,
        data=gdf_focus,
        columns=[name_col, choropleth_col],
        key_on=f"feature.properties.{name_col}",
        fill_color="YlGnBu",
        fill_opacity=0.9,
        line_opacity=0.3,
        highlight=False,
        name=f"{choropleth_col.replace('_', ' ')} (districts)",
    ).add_to(m)

    # GeoJson-layer for popups
    folium.GeoJson(
        gdf_focus,
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

    # Ensures valid CRS
    building = CRS(buildings_gdf, target_crs="EPSG:4326", name="buildings_gdf", wgs84_missing=True,)

    # Checks that specified districts exist in buildings_gdf
    if building_district_col not in building.columns:
        raise KeyError(f"Column {building_district_col!r} does not exist in buildings_gdf.")
    if building_type_col not in building.columns:
        raise KeyError(f"Column {building_type_col!r} does not exist in buildings_gdf.")

    # Filters buildings to the selected districts
    building = building[building[building_district_col].isin(focus)].copy()

    if len(building) == 0:
        raise ValueError("There are no buildings in the selected districts.")

    # Håndterer manglende bygningstype
    # Handles missing building type
    building[building_type_col] = building[building_type_col].fillna("unknown")
    building_types = sorted(building[building_type_col].unique())

    # Fargemapping
    base_colors = [
        "#1b9e77", "#d95f02", "#7570b3", "#e7298a",
        "#66a61e", "#e6ab02", "#a6761d", "#666666",
        "#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6",
    ]
    type_to_color = {
        t: base_colors[i % len(base_colors)]
        for i, t in enumerate(building_types)
    }

    # Separate layer for building types
    fg_building = folium.FeatureGroup(name="Building types", show=False)

    # Adding each building
    for _, row in building.iterrows():
        btype = row[building_type_col]
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
            tooltip=folium.Tooltip(f"<b>Building type:</b> {btype}"),
        ).add_to(fg_building)

    fg_building.add_to(m)

    
    folium.LayerControl(collapsed=False).add_to(m)
    return m