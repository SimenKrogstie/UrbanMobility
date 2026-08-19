"""Shared pytest fixtures: synthetic districts/buildings GeoDataFrames."""

import matplotlib

matplotlib.use("Agg")

import geopandas as gpd
import pandas as pd
from shapely.geometry import box, Point, LineString, MultiPolygon, Polygon
import pytest

from urbanmobility.config import DEFAULT_CRS

# Real Oslo-area UTM33N coordinates so WGS84 round-trips used for
# CRS-reprojection tests land inside these district boundaries.
DISTRICT_A_BOUNDS = (597000, 6643000, 598000, 6644000)  # 1000m x 1000m = 1 km^2
DISTRICT_B_BOUNDS = (599000, 6643000, 599500, 6644000)  # 500m x 1000m = 0.5 km^2

# Buildings inside district A: 20x20 (400 m^2) and 30x30 (900 m^2) -> 1300 m^2 total
BUILDING_A1_BOUNDS = (597100, 6643100, 597120, 6643120)
BUILDING_A2_BOUNDS = (597200, 6643200, 597230, 6643230)
# Building inside district B: 50x50 (2500 m^2)
BUILDING_B1_BOUNDS = (599100, 6643100, 599150, 6643150)


@pytest.fixture
def districts_gdf() -> gpd.GeoDataFrame:
    """Two districts, 'A' (1 km^2) and 'B' (0.5 km^2), with known areas."""
    return gpd.GeoDataFrame(
        {"bydel": ["A", "B"]},
        geometry=[box(*DISTRICT_A_BOUNDS), box(*DISTRICT_B_BOUNDS)],
        crs=DEFAULT_CRS,
    )


@pytest.fixture
def buildings_gdf() -> gpd.GeoDataFrame:
    """Buildings already joined to districts_gdf, with known individual areas."""
    return gpd.GeoDataFrame(
        {"bydel": ["A", "A", "B"]},
        geometry=[
            box(*BUILDING_A1_BOUNDS),
            box(*BUILDING_A2_BOUNDS),
            box(*BUILDING_B1_BOUNDS),
        ],
        crs=DEFAULT_CRS,
    )


@pytest.fixture
def raw_osm_buildings_gdf() -> gpd.GeoDataFrame:
    """Mixed geometry types with no CRS set, simulating raw OSM output."""
    return gpd.GeoDataFrame(
        {"element": ["polygon", "multipolygon", "point", "line"]},
        geometry=[
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            MultiPolygon(
                [
                    Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
                    Polygon([(4, 0), (5, 0), (5, 1), (4, 1)]),
                ]
            ),
            Point(6, 0),
            LineString([(7, 0), (8, 1)]),
        ],
    )


@pytest.fixture
def invalid_geometry_gdf() -> gpd.GeoDataFrame:
    """A self-intersecting (bowtie) polygon."""
    bowtie = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])
    return gpd.GeoDataFrame({"bydel": ["A"]}, geometry=[bowtie], crs=DEFAULT_CRS)


@pytest.fixture
def empty_geometry_gdf() -> gpd.GeoDataFrame:
    """A geometry column containing an empty Polygon."""
    return gpd.GeoDataFrame({"bydel": ["A"]}, geometry=[Polygon()], crs=DEFAULT_CRS)


@pytest.fixture
def mobility_districts_gdf() -> gpd.GeoDataFrame:
    """Districts 'A' and 'B' (same geometry as districts_gdf) with population,
    for mobility indicators: A=2000 people / 1 km^2, B=1500 people / 0.5 km^2 ->
    population_density A=2000, B=3000 (distinct, so bugs swapping A/B surface)."""
    return gpd.GeoDataFrame(
        {"bydel": ["A", "B"], "befolkning_2024": [2000, 1500]},
        geometry=[box(*DISTRICT_A_BOUNDS), box(*DISTRICT_B_BOUNDS)],
        crs=DEFAULT_CRS,
    )


@pytest.fixture
def trips_df() -> pd.DataFrame:
    """Trips between districts 'A' and 'B' with known start/end counts and hours.

    start_district: A,A,A,B,B,B,B -> started A=3, B=4
    end_district:   A,B,B,A,B,B,B -> ended   A=2, B=5
    => net_trips: A=-1 (negative), B=+1 (positive) - covers both the red/green
    bar-coloring branches in plot_mobility_indicators.

    started_at hours: A-starts at 8,8,9; B-starts at 10,10,11,11 - spread across
    distinct hours so plot_timeprofile/plot_timeprofile_directions counts are
    individually verifiable.
    """
    return pd.DataFrame(
        {
            "start_district": ["A", "A", "A", "B", "B", "B", "B"],
            "end_district": ["A", "B", "B", "A", "B", "B", "B"],
            "started_at": pd.to_datetime(
                [
                    "2025-10-01T08:00:00Z",
                    "2025-10-01T08:30:00Z",
                    "2025-10-01T09:00:00Z",
                    "2025-10-01T10:00:00Z",
                    "2025-10-01T10:30:00Z",
                    "2025-10-01T11:00:00Z",
                    "2025-10-01T11:30:00Z",
                ]
            ),
        }
    )


@pytest.fixture
def building_types_gdf() -> gpd.GeoDataFrame:
    """Buildings across both districts with a 'building' type column, incl. a NaN."""
    return gpd.GeoDataFrame(
        {
            "bydel": ["A", "A", "A", "B", "B"],
            "building": ["house", "house", "apartments", None, "commercial"],
        },
        geometry=[
            box(597100, 6643100, 597110, 6643110),
            box(597120, 6643120, 597130, 6643130),
            box(597140, 6643140, 597150, 6643150),
            box(599100, 6643100, 599110, 6643110),
            box(599120, 6643120, 599130, 6643130),
        ],
        crs=DEFAULT_CRS,
    )
