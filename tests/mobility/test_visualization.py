import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pytest

from urbanmobility.config import MOBILITY_INDICATORS, NET_TRIPS
from urbanmobility.mobility.indicators import calculate_mobility_indicators
from urbanmobility.mobility.visualization import (
    plot_mobility_indicators,
    plot_timeprofile,
    plot_timeprofile_directions,
)


@pytest.fixture
def mobility_gdf(mobility_districts_gdf, trips_df):
    return calculate_mobility_indicators(mobility_districts_gdf, trips_df)


def _ydata(line) -> list[float]:
    """matplotlib's stubs type Line2D.get_ydata() as ArrayLike, which has no
    __getitem__, even though it's a numpy array at runtime."""
    return list(line.get_ydata())  # type: ignore[arg-type]


# --- plot_mobility_indicators --------------------------------------------------


def test_plot_mobility_indicators_rejects_missing_indicator_column(
    mobility_districts_gdf,
):
    with pytest.raises(KeyError):
        plot_mobility_indicators(mobility_districts_gdf.set_index("bydel"), "A", "B")


def test_plot_mobility_indicators_rejects_absent_district(mobility_gdf):
    with pytest.raises(KeyError):
        plot_mobility_indicators(mobility_gdf, "A", "C")


def test_plot_mobility_indicators_returns_figure_with_one_axis_per_indicator(
    mobility_gdf,
):
    fig = plot_mobility_indicators(mobility_gdf, "A", "B")

    try:
        visible_axes = [ax for ax in fig.axes if ax.get_visible()]
        assert len(visible_axes) == len(MOBILITY_INDICATORS)
    finally:
        plt.close(fig)


def test_plot_mobility_indicators_colors_negative_red_and_positive_green(mobility_gdf):
    fig = plot_mobility_indicators(mobility_gdf, "A", "B")

    try:
        # District A has net_trips=-1 (red), district B has net_trips=+1 (green) -
        # see tests/conftest.py's trips_df fixture docstring.
        net_trips_index = list(MOBILITY_INDICATORS).index(NET_TRIPS)
        patches = fig.axes[net_trips_index].patches

        assert mcolors.same_color(patches[0].get_facecolor(), "tab:red")
        assert mcolors.same_color(patches[1].get_facecolor(), "green")
    finally:
        plt.close(fig)


# --- plot_timeprofile -----------------------------------------------------------


def test_plot_timeprofile_rejects_missing_columns(trips_df):
    trips = trips_df.drop(columns=["start_district"])
    with pytest.raises(KeyError):
        plot_timeprofile(trips, "A", "B")


def test_plot_timeprofile_returns_figure_with_two_axes(trips_df):
    fig = plot_timeprofile(trips_df, "A", "B")

    try:
        assert len(fig.axes) == 2
    finally:
        plt.close(fig)


def test_plot_timeprofile_aggregates_counts_per_hour(trips_df):
    fig = plot_timeprofile(trips_df, "A", "B")

    try:
        line_a, line_b = fig.axes[0].get_lines()
        # A starts: hour 8 -> 2 trips, hour 9 -> 1 trip (see conftest.py)
        assert _ydata(line_a)[8] == 2
        assert _ydata(line_a)[9] == 1
        # B starts: hour 10 -> 2 trips, hour 11 -> 2 trips
        assert _ydata(line_b)[10] == 2
        assert _ydata(line_b)[11] == 2
    finally:
        plt.close(fig)


def test_plot_timeprofile_parses_string_time_column(trips_df):
    trips = trips_df.copy()
    trips["started_at"] = trips["started_at"].astype(str)

    fig = plot_timeprofile(trips, "A", "B")

    try:
        line_a, _ = fig.axes[0].get_lines()
        assert _ydata(line_a)[8] == 2
    finally:
        plt.close(fig)


# --- plot_timeprofile_directions -------------------------------------------------


def test_plot_timeprofile_directions_rejects_missing_columns(trips_df):
    trips = trips_df.drop(columns=["end_district"])
    with pytest.raises(KeyError):
        plot_timeprofile_directions(trips, "A", "B")


def test_plot_timeprofile_directions_returns_figure_with_two_lines(trips_df):
    fig = plot_timeprofile_directions(trips_df, "A", "B")

    try:
        assert len(fig.axes[0].get_lines()) == 2
    finally:
        plt.close(fig)


def test_plot_timeprofile_directions_counts_match_expected(trips_df):
    fig = plot_timeprofile_directions(trips_df, "A", "B")

    try:
        line_ab, line_ba = fig.axes[0].get_lines()
        # A -> B trips: hour 8 -> 1, hour 9 -> 1 (see conftest.py)
        assert _ydata(line_ab)[8] == 1
        assert _ydata(line_ab)[9] == 1
        # B -> A trips: hour 10 -> 1
        assert _ydata(line_ba)[10] == 1
    finally:
        plt.close(fig)
