"""Configuration for urbanmobility."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2].resolve()

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA = {
    "trips": DATA_DIR / "raw" / "sykkel_oktober_2025.csv",
    "districts": DATA_DIR / "raw" / "oslo_bydeler_befolkning_2024.geojson",
}

# CRS constants
DEFAULT_CRS = "EPSG:28533"
CRS_WGS84 = "EPSG:4326"

# Buildings constants
AREA_M2 = "area_m2"
AREA_KM2 = "area_km2"

BUILDING_COUNT = "num_buildings"
BUILDING_AREA = "building_area_m2"
BUILDING_DENSITY = "buildings_per_km2"
BUILT_AREA_PERCENT = "built_up_area_percent"
AVG_BUILDING_AREA = "avg_building_area_m2"

BUILDING_INDICATORS = (
    BUILDING_COUNT,
    BUILDING_AREA,
    BUILDING_DENSITY,
    BUILT_AREA_PERCENT,
    AVG_BUILDING_AREA,
)