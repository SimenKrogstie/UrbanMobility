"""Building visualiozation functions."""

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np

from .validation import (
    validate_indicators,
    validate_districts_exist,
    validate_building_plot_data,
)

from ..config  import (
    BUILDING_COUNT,
    BUILDING_AREA,
    BUILDING_DENSITY,
    BUILT_AREA_PERCENT,
    AVG_BUILDING_AREA,
)



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
    BUILDING_INDICATORS = [
        BUILDING_COUNT,
        BUILDING_AREA,
        BUILDING_DENSITY,
        BUILT_AREA_PERCENT,
        AVG_BUILDING_AREA,
    ]

    # Validate input 
    validate_indicators(building_indicators_gdf, BUILDING_INDICATORS)
    validate_districts_exist(building_indicators_gdf, [district_a, district_b], district_col)

    df = building_indicators_gdf.loc[
        [district_a, district_b]
    ]

    districts = [
        district_a,
        district_b
    ]

    # Size of subplot
    n = len(BUILDING_INDICATORS)
    cols = 3
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(4 * cols, 4 * rows),
        squeeze=False
    )

    axes = axes.flatten()

    for ax, indicator in zip(
        axes,
        BUILDING_INDICATORS
    ):
        values = df[indicator].values

        ax.bar(districts, values, zorder=3)
        ax.set_title(indicator.replace("_", " "))
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    # Hide unused subplot axes
    for ax in axes[len(BUILDING_INDICATORS):]:
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

    # Validate input
    validate_building_plot_data(buildings_gdf, district_col, type_col)
    validate_districts_exist(buildings_gdf, [district_a, district_b], district_col)

    districts = [
        district_a,
        district_b
    ]

    df = buildings_gdf.copy()

    df[type_col] = (
        df[type_col]
        .fillna("unknown")
    )

    df = df[
        df[district_col]
        .isin(districts)
    ]

    available_types = (
        df[type_col]
        .value_counts()
    )

    if types is None:
        types = list(
            available_types.index
        )
    else:
        types = [
            t for t in types
            if t in available_types.index
        ]

    if not types:
        raise ValueError(
            "No building types available for plotting."
        )
    
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(9,5),
        sharex=True,
        sharey=not normalize
    )

    axes = axes.flatten()

    for ax, district in zip(
        axes,
        districts
    ):
        subset = df[
            df[district_col] == district
        ]

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
                counts = (
                    counts / total * 100
                )

        ax.bar(counts.index, counts.values)
        ax.set_title(f"Building types in {district}" + (" (%)" if normalize else ""))
        ax.set_ylabel("Percentage" if normalize else "Number of buildings")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, linestyle="--", alpa=0.6)

    plt.tight_layout()

    return fig