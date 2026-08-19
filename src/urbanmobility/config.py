from pathlib import Path

PROJECT_ROOT = Path(__file__).parents(2).resolve()
DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA = {
    "trips": DATA_DIR / "raw"/"sykkel_oktober_2025.csv",
    "districts": DATA_DIR / "raw"/"oslo_bydeler_befolkning_2024.geojson",
}

CRS_WGS84 = "EPSG:4326"
CRS_OSLO = "EPSG:28533"