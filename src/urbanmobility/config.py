"""Configuration for urbanmobility."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2].resolve()

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA = {
    "trips": DATA_DIR / "raw" / "sykkel_oktober_2025.csv",
    "districts": DATA_DIR / "raw" / "oslo_bydeler_befolkning_2024.geojson",
}

# CRS constants
DEFAULT_CRS = "EPSG:25833"
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

# Mobility constants
POPULATION_DENSITY = "population_density_km2"
TRIPS_STARTED = "trips_started"
TRIPS_ENDED = "trips_ended"
NET_TRIPS = "net_trips"
TOTAL_TRIPS = "total_trips"
TRIPS_STARTED_PER_KM2 = "trips_started_per_km2"
TRIPS_ENDED_PER_KM2 = "trips_ended_per_km2"
NET_TRIPS_PER_KM2 = "net_trips_per_km2"
TOTAL_TRIPS_PER_KM2 = "total_trips_per_km2"
TRIPS_STARTED_PER_CAPITA = "trips_started_per_capita"
TRIPS_ENDED_PER_CAPITA = "trips_ended_per_capita"
NET_TRIPS_PER_CAPITA = "net_trips_per_capita"
TOTAL_TRIPS_PER_CAPITA = "total_trips_per_capita"

MOBILITY_INDICATORS = (
    TRIPS_STARTED,
    TRIPS_ENDED,
    NET_TRIPS,
    TOTAL_TRIPS,
    TRIPS_STARTED_PER_KM2,
    TRIPS_ENDED_PER_KM2,
    NET_TRIPS_PER_KM2,
    TOTAL_TRIPS_PER_KM2,
    TRIPS_STARTED_PER_CAPITA,
    TRIPS_ENDED_PER_CAPITA,
    NET_TRIPS_PER_CAPITA,
    TOTAL_TRIPS_PER_CAPITA,
    POPULATION_DENSITY,
)
