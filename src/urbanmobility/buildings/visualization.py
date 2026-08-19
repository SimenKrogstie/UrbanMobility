"""Building visualization functions."""

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import geopandas as gpd

from .validation import (
    validate_indicators,
    validate_districts_exist,
    validate_building_plot_data,
)

from ..config import BUILDING_INDICATORS


def _resolve_building_types(
    gdf: gpd.GeoDataFrame,
    type_col: str,
    requested_types: list[str] | None = None,
) -> list[str]:
    """
    Return valid buildingtypes available in the dataset.
    """
    available = gdf[type_col].value_counts().index

    types = (
        list(available)
        if requested_types is None
        else [t for t in requested_types if t in available]
    )

    if not types:
        raise ValueError("No building types available for plotting.")

    return types


def plot_building_indicators(
    building_indicators_gdf: gpd.GeoDataFrame,
    district_a: str,
    district_b: str,
    district_col: str = "bydel",
) -> Figure:
    """
    Plot comparison of building indicators between two districts.

    Parameters
    ----------
    buildingindicators_gdf : gpd.GeoDataFrame
        GeoDataFrame containing calculated indicators.
    district_a : str
        First district name.
    district_b : str
        Second district name.
    district_col : str, default = "bydel"
        Column containing district names.

    Returns
    -------
    Figure
        Matplotlib Figure containing indicator comparisons.

    """
    # Districts in focus
    focus = (district_a, district_b)

    # Validate input
    validate_indicators(building_indicators_gdf, BUILDING_INDICATORS)
    validate_districts_exist(building_indicators_gdf, focus, district_col)
    df = building_indicators_gdf.loc[list(focus)]

    # Size of subplot
    cols = 3
    rows = (len(BUILDING_INDICATORS) + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows), squeeze=False)

    axes = axes.flatten()

    for ax, indicator in zip(axes, BUILDING_INDICATORS):
        values = df[indicator].values

        ax.bar(focus, values, zorder=3)
        ax.set_title(indicator.replace("_", " "))
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    # Hide unused subplot axes
    for ax in axes[len(BUILDING_INDICATORS) :]:
        ax.set_visible(False)

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
    Plot distribution of buiolding types between two districts.


    Parameters
    ----------
    buildings_gdf : gpd.GeoDataFrame
        Building dataset containing district and type columns.
    district_a : str
        First district name.
    district_b : str
        Second district name.
    district_col : str, default = "bydel"
        Column containing district names.
    type_col : str, default="building"
        Column containing building types.
    types : list of str or None, optional
        Building types to include.
    normalize : bool, optional
        If True, show percentage distribution.

    Returns
    -------
    Figure
        Matplotlib Figure showing building type distribution.


    """

    # Districts to focus on
    focus = (district_a, district_b)

    # Validate input
    validate_building_plot_data(buildings_gdf, district_col, type_col)
    validate_districts_exist(buildings_gdf, focus, district_col)

    df = buildings_gdf[buildings_gdf[district_col].isin(focus)].copy()
    df[type_col] = df[type_col].fillna("unknown")

    types = _resolve_building_types(df, type_col, types)

    fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True, sharey=not normalize)
    axes = axes.flatten()

    groups = df.groupby(district_col)

    for ax, district in zip(axes, focus):
        subset = groups.get_group(district)
        counts = (
            subset[type_col]
            .value_counts()
            .reindex(
                types,
                fill_value=0,
            )
        )

        if normalize:
            total = counts.sum()

            if total > 0:
                counts = counts / total * 100

        ax.bar(counts.index, counts.values)
        ax.set_title(f"Building types in {district}" + (" (%)" if normalize else ""))
        ax.set_ylabel("Percentage" if normalize else "Number of buildings")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()

    return fig
