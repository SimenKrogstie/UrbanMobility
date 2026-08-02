"""Building data processing and analysis."""

from .processing import get_osm_buildings
from .indicators import calculate_building_indicators
from .visualization import (
    plot_building_indicators,
    plot_building_types,
)

__all__ = [
    "get_osm_buildings",
    "calculate_building_indicators",
    "plot_building_indicators",
    "plot_building_types",
]
