from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np

def plot_building_indicators(
        buildingindicators_gdf: gpd.GeoDataFrame,
        district_a: str,
        district_b: str
) -> Figure:
    """
    Visualize building indicators for two selected districts with bar plots.

    The function makes a grid of bar plots where each indicator is shown for
    distrrict_a and district_b. Colors indicate negative values (red) or 
    positive values (green).

    Indicators that are plotted:
        - number of buildings
        - buildingarea (m^2)
        - number of buildings per km^2
        - built-up area in percent
        - average size of buildings (m^2)

    Parameters
    ----------
    buildingindicators_gdf : gpd.GeoDataFrame
        GeoDataFrame with building indicators.
    district_a : str
        Name of the first district to compare.
    district_b : str
        Name of the second district to compare.

    Returns
    -------
    fig : Figure
        Figure with bar plots for each indicator.
    
    Raises
    ------
    KeyError
        If one of the districts or indicators does not exist.
    """

    # Checks that the districts exist
    for i in [district_a, district_b]:
        if i not in buildingindicators_gdf.index:
            raise KeyError(f"District {i!r} does not exist in buildingindicators_gdf.")

    df = buildingindicators_gdf.loc[[district_a, district_b]].copy()

    # Indicators to be visualized
    indicators = [
        "num_buildings",
        "building_area_m2",
        "buildings_per_km2",
        "built_up_area_percent",
        "avg_building_area_m2"
    ]

    # Checks that all indicators exist
    for col in indicators:
        if col not in buildingindicators_gdf.columns:
            raise KeyError(f"Column {col!r} does not exist in GeoDataFrame.")

    districts = [district_a, district_b]

    # Size of subplot
    n = len(indicators)
    cols = 3
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    axes = axes.flatten()

    # Plot each indicator in its own subplot
    for i, ind in enumerate(indicators):
        ax = axes[i]

        values = df[ind].values
        colors = ["tab:red" if v < 0 else "green" for v in values]

        ax.bar(districts, values, color=colors, zorder=3)
        ax.set_title(ind.replace("_", " "), fontsize=11)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    # Hide empty plots
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    return fig


def plot_building_types(
        buildings_gdf: gpd.GeoDataFrame,
        district_a: str,
        district_b: str,
        district_col: str = "bydel",
        type_col: str = "building",
        types: list[str] | None = None,
        normalize: bool = False,
) -> Figure:
    """
    Plots the distribution of building types between two selected districts.

    For each of the two districts, a bar plot is created where each bar represents
    a building type. Colors are consistent across districts.

    If "normalize=True", the bars are normalized to percentage per district.


    Parameters
    ----------
    buildings_gdf : gpd.GeoDataFrame
        GeoDataFrame with buildings.
    district_a : str
        Name of the first district to compare.
    district_b : str
        Name of the second district to compare.
    district_col : str, optional
        Name of the column in "buildings_gdf" with district names.
        Default is "bydel".
    type_col : str, optional
        Name of the column for building type (e.g., OSM "building"-tag).
        Default is "building".
    types : list of str or None, optional
        List of building types to include in the plot.
        If None, all building types present in the data are included.
    normalize : bool, optional
        If True, the bars are normalized to percentage per district.
        If False, the bars show counts of buildings.
        Default is False.

    Returns
    -------
    fig : Figure
        Figure showing the distribution of building types per district.
    
    Raises 
    ------
    KeyError
        If "district_col" or "type_col" is missing in "buildings_gdf",
        or if one of the specified districts does not exist in the dataset.
    ValueError
        If no building types are available to plot after filtering.
    """

    # Checks that the necessary columns exist
    if district_col not in buildings_gdf.columns:
        raise KeyError(f"Column {district_col!r} does not exist in GeoDataFrame.")
    if type_col not in buildings_gdf.columns:
        raise KeyError(f"Column {type_col!r} does not exist in GeoDataFrame.")

    # Checks that the districts exist
    focus = [district_a, district_b]
    for d in focus:
        if d not in buildings_gdf[district_col].unique():
            raise KeyError(f"District {d!r} does not exist in the dataset.")

    # Filters to selected districts and handles missing building types
    df = buildings_gdf.copy()
    df[type_col] = df[type_col].fillna("uknown")
    df = df[df[district_col].isin(focus)]

    # Counts relevant building types
    total_counts = df[type_col].value_counts()

    if types is not None:
        types = [t for t in types if total_counts.get(t, 0) > 0]
    else:
        types = [t for t, c in total_counts.items() if c > 0]

    if len(types) == 0:
        raise ValueError("No building types to show after filtering.")

    # Colormap for building types
    base_colors = [
        "#1b9e77", "#d95f02", "#7570b3", "#e7298a",
        "#66a61e", "#e6ab02", "#a6761d", "#666666",
        "#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6"
    ]
    type_to_color = {t: base_colors[i % len(base_colors)] for i, t in enumerate(types)}

    fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True, sharey=not normalize)
    axes = axes.flatten()

    # Plots for each district
    for ax, district in zip(axes, focus):
        subset = df[df[district_col] == district]
        counts = subset[type_col].value_counts().reindex(types, fill_value=0)

        if normalize:
            total = counts.sum()
            if total > 0:
                counts = counts / total * 100

        colors = [type_to_color[t] for t in counts.index]

        ax.bar(counts.index, counts.values, color=colors, edgecolor="black")

        ax.set_title(f"Building types in {district}" + (" (%)" if normalize else ""), fontsize=13)
        ax.set_ylabel("Percentage" if normalize else "Number of buildings")
        ax.tick_params(axis="x", rotation=45)

        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    plt.tight_layout()
    return fig