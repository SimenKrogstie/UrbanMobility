import geopandas as gpd
import pandas as pd
from ..crs import CRS
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def plot_mobility_indicators(
        mobility_gdf: gpd.GeoDataFrame,
        district_a: str,
        district_b: str
    ) -> Figure:
    """
    Plots a set of mobility indicators as bar plots for two selected districts.

    The function creates one subplot per indicator and shows:
        - Number of trips (started/ended/net/total)
        - Trips per km^2
        - Trips per capita
        - Population density

    Negative indicators are marked in red, positive in green.

    Parameters
    ----------
    mobility_gdf : gpd.GeoDataFrame
        GeoDataFrame with mobility indicators.
    district_a : str
        Name of the first district to compare.
    district_b : str
        Name of the second district to compare.
        
    Returns
    -------
    fig : Figure
        Figure with subplots for each indicator.

    Raises
    ------
    KeyError
        If one of the specified districts does not exist in "mobility_gdf.index".

    """

    # Checks that the districts exist
    for i in [district_a, district_b]:
        if i not in mobility_gdf.index:
            raise KeyError(f"District {i!r} does not exist in mobility_gdf.")

    # Filters on the selected districts
    df = mobility_gdf.loc[[district_a, district_b]].copy()

    # Indicators to be visualized
    indicators = [
        "trips_started", "trips_ended", "net_trips", "total_trips",
        "trips_started_per_km2", "trips_ended_per_km2", "net_trips_per_km2", "total_trips_per_km2",
        "trips_started_per_capita", "trips_ended_per_capita",
        "net_trips_per_capita", "total_trips_per_capita",
        "population_density_km2"
    ]

    districts = [district_a, district_b]

    # Size for subplot
    n = len(indicators)
    cols = 4
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
    axes = axes.flatten()

    # Plots each indicator in its own subplot
    for i, ind in enumerate(indicators):
        ax = axes[i]

        values = df[ind].values
        colors= ["tab:red" if v < 0 else "green" for v in values]

        ax.bar(districts, values, color=colors, zorder=3)
        ax.set_title(ind.replace("_", " "), fontsize=11)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, linestyle="--", alpha=0.6, zorder=0)

    # Hide empty plots
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    return fig


def plot_timeprofile(
        trips_df: pd.DataFrame,
        district_a: str,
        district_b: str,
        start_col: str = "start_district",
        end_col: str = "end_district",
        time_column: str = "started_at",
) -> Figure:
    """
    Plots time profiles (per hour) for two districts.
    
    The function creates a figure with two subplots:
    - Left: number of trips per hour starting in each district.
    - Right: number of trips per hour ending in each district.

    Parameters
    ----------
    trips_df : pd.DataFrame
        DataFrame with trip data.
    district_a : str
        Name of the first district to compare.
    district_b : str
        Name of the second district to compare.
    start_col : str, optional
        Name of the column in "trips_df" with start district.
        Default is "start_district".
    end_col : str, optional
        Name of the column in "trips_df" with end district.
        Default is "end_district"
    time_column : str, optional
        Name of the column in "trips_df" with start time for the trip.
        Default is "started_at".

    Returns
    -------
    fig : Figure
        Figure with two line plots showing start and end of trips per hour.
    
    Raises
    ------
    KeyError
        If "start_col", "end_col" or "time_column" is missing in "trips_df".
    """
    df = trips_df.copy()

    # Checks that necessary columns exist
    for col in [start_col, end_col, time_column]:
        if col not in df.columns:
            raise KeyError(f"Column {col!r} is missing in trips_df.")

    # Ensures datetime
    if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
        df[time_column] = pd.to_datetime(df[time_column], errors="coerce", utc=True)

    # Removes rows without valid time and adds a column for time of day
    df = df.dropna(subset=[time_column])
    df["time"] = df[time_column].dt.hour

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharex=True)
    ax_start = axes[0]
    ax_slutt = axes[1]

    districts = [district_a, district_b]
    colors = ["tab:blue", "tab:orange"]

    # Start of biketrips
    for district, color in zip(districts, colors):
        df_start = df[df[start_col] == district]
        num_start = df_start.groupby("time").size().reindex(range(24), fill_value=0)

        ax_start.plot(
            num_start.index,
            num_start.values,
            marker="o",
            color=color,
            label=f"{district}")

    ax_start.set_title("Trips starting in the districts")
    ax_start.set_xlabel("Time of day")
    ax_start.set_ylabel("Number of trips")
    ax_start.grid(True, linestyle="--", alpha=0.6)
    ax_start.legend(title="District")

    # End of biketrips
    for district, color in zip(districts, colors):
        df_slutt = df[df[end_col] == district]
        num_slutt = df_slutt.groupby("time").size().reindex(range(24), fill_value=0)

        ax_slutt.plot(
            num_slutt.index,
            num_slutt.values,
            marker="o",
            color=color,
            label=f"{district}")

    ax_slutt.set_title("Trips ending in the districts")
    ax_slutt.set_xlabel("Time of day")
    ax_slutt.set_ylabel("Number of trips")
    ax_slutt.grid(True, linestyle="--", alpha=0.6)
    ax_slutt.legend(title="District")

    plt.tight_layout()
    return fig


def plot_timeprofile_directions(
        trips_df: pd.DataFrame,
        district_a: str,
        district_b: str,
        start_col: str = "start_district",
        end_col: str = "end_district",
        time_column: str = "started_at",
) -> Figure:
    """
    Plots time profile (per hour) for trips between two districts in both directions.

    Two lines are plotted:
    - trips from district_a to district_b
    - trips from district_b to district_a

    Parameters
    ----------
    trips_df : pd.DataFrame
        DataFrame with trip data.
    district_a : str
        Name of the first district to compare.
    district_b : str
        Name of the second district to compare.
    start_col : str, optional
        Name of the column in "trips_df" with start district.
        Default is "start_district"
    end_col : str, optional
        Name of the column in "trips_df" with end district.
        Default is "end_district"
    time_column : str, optional
        Name of the column in "trips_df" with start time for the trip.
        Default is "started_at".

    Returns
    -------
    fig : Figure
        Figure with line plot showing time profile for both directions.
    
    Raises
    ------
    KeyError
        If required columns are missing in "trips_df".
    """
    df = trips_df.copy()

    # Checks that necessary columns exist
    for col in [start_col, end_col, time_column]:
        if col not in df.columns:
            raise KeyError(f"Column {col!r} is missing in trips_df.")

    # Ensures datetime
    if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
        df[time_column] = pd.to_datetime(df[time_column], errors="coerce", utc=True)

    # Removes rows without valid time and adds column for time of day
    df = df.dropna(subset=[time_column])
    df["time"] = df[time_column].dt.hour

    fig, ax = plt.subplots(figsize=(10,5))

    # Defines directions
    directions = [
        (district_a, district_b, "tab:blue"),
        (district_b, district_a, "tab:orange")
    ]

    for start_district, end_district, color in directions:
        df_dir = df[(df[start_col] == start_district) & (df[end_col] == end_district)]
        count = df_dir.groupby("time").size().reindex(range(24), fill_value=0)

        ax.plot(
            count.index,
            count.values,
            marker="o",
            color=color,
            label=f"{start_district} -> {end_district}"
        )

    ax.set_xlabel("Time of day")
    ax.set_ylabel("Number of trips")
    ax.set_title(f"Time profile for trips between {district_a} and {district_b}")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    
    return fig