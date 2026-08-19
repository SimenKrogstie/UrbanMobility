import matplotlib.pyplot as plt
import pytest

from urbanmobility.buildings.indicators import calculate_building_indicators
from urbanmobility.buildings.visualization import (
    _resolve_building_types,
    plot_building_indicators,
    plot_building_types,
)
from urbanmobility.config import BUILDING_INDICATORS


def _bar_heights(ax) -> list[float]:
    """Heights of the bars drawn on an axis (matplotlib's stubs type
    ax.containers[0] as the base Container, which has no .datavalues, even
    though bar() always attaches a BarContainer at runtime)."""
    return list(ax.containers[0].datavalues)  # type: ignore[attr-defined]


# --- _resolve_building_types ---------------------------------------------------


def test_resolve_building_types_returns_all_when_none_requested(building_types_gdf):
    types = _resolve_building_types(building_types_gdf, "building")

    assert set(types) == {"house", "apartments", "commercial"}


def test_resolve_building_types_filters_to_overlap(building_types_gdf):
    types = _resolve_building_types(
        building_types_gdf, "building", ["house", "not_a_type"]
    )

    assert types == ["house"]


def test_resolve_building_types_raises_when_no_overlap(building_types_gdf):
    with pytest.raises(ValueError):
        _resolve_building_types(building_types_gdf, "building", ["not_a_type"])


# --- plot_building_indicators --------------------------------------------------


@pytest.fixture
def building_indicators_gdf(buildings_gdf, districts_gdf):
    return calculate_building_indicators(buildings_gdf, districts_gdf)


def test_plot_building_indicators_rejects_missing_indicator_column(districts_gdf):
    with pytest.raises(KeyError):
        plot_building_indicators(districts_gdf.set_index("bydel"), "A", "B")


def test_plot_building_indicators_rejects_absent_district(building_indicators_gdf):
    with pytest.raises(KeyError):
        plot_building_indicators(building_indicators_gdf, "A", "C")


def test_plot_building_indicators_returns_figure_with_one_axis_per_indicator(
    building_indicators_gdf,
):
    fig = plot_building_indicators(building_indicators_gdf, "A", "B")

    try:
        visible_axes = [ax for ax in fig.axes if ax.get_visible()]
        assert len(visible_axes) == len(BUILDING_INDICATORS)
    finally:
        plt.close(fig)


# --- plot_building_types --------------------------------------------------------


def test_plot_building_types_rejects_missing_type_col(buildings_gdf):
    with pytest.raises(KeyError):
        plot_building_types(buildings_gdf, "A", "B", type_col="not_a_column")


def test_plot_building_types_rejects_absent_district(building_types_gdf):
    with pytest.raises(KeyError):
        plot_building_types(building_types_gdf, "A", "C")


def test_plot_building_types_buckets_nan_as_unknown(building_types_gdf):
    fig = plot_building_types(building_types_gdf, "A", "B")

    try:
        b_axis_labels = {label.get_text() for label in fig.axes[1].get_xticklabels()}
        assert "unknown" in b_axis_labels
    finally:
        plt.close(fig)


def test_plot_building_types_filters_to_requested_types(building_types_gdf):
    fig = plot_building_types(building_types_gdf, "A", "B", types=["house"])

    try:
        # District A has 2 "house" buildings and no other requested types,
        # so exactly one bar (for "house") should be drawn.
        heights = _bar_heights(fig.axes[0])
        assert len(heights) == 1
        assert heights[0] == 2
    finally:
        plt.close(fig)


def test_plot_building_types_raises_when_requested_types_have_no_overlap(
    building_types_gdf,
):
    with pytest.raises(ValueError):
        plot_building_types(building_types_gdf, "A", "B", types=["not_a_type"])


def test_plot_building_types_normalize_handles_zero_buildings_without_nan(
    building_types_gdf,
):
    # District B has no "apartments" buildings; restricting to that type
    # leaves B with zero matching buildings after filtering.
    fig = plot_building_types(
        building_types_gdf, "A", "B", types=["apartments"], normalize=True
    )

    try:
        b_bar_heights = _bar_heights(fig.axes[1])
        assert all(height == 0 for height in b_bar_heights)
        assert not any(h != h for h in b_bar_heights)  # not NaN
    finally:
        plt.close(fig)


def test_plot_building_types_normalize_produces_percentages(building_types_gdf):
    fig = plot_building_types(building_types_gdf, "A", "B", normalize=True)

    try:
        a_total = sum(_bar_heights(fig.axes[0]))
        assert a_total == pytest.approx(100.0)
    finally:
        plt.close(fig)


def test_plot_building_types_without_normalize_returns_raw_counts(building_types_gdf):
    fig = plot_building_types(building_types_gdf, "A", "B", normalize=False)

    try:
        a_total = sum(_bar_heights(fig.axes[0]))
        assert a_total == pytest.approx(3)  # 3 buildings in district A
    finally:
        plt.close(fig)


def test_plot_building_types_returns_figure_with_one_axis_per_district(
    building_types_gdf,
):
    fig = plot_building_types(building_types_gdf, "A", "B")

    try:
        assert len(fig.axes) == 2
    finally:
        plt.close(fig)
