from unittest.mock import patch

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box

from urbanmobility.buildings.processing import (
    _filter_building_geometries,
    get_osm_buildings,
)
from urbanmobility.config import DEFAULT_CRS


def _reprojected_wgs84_square(easting: float, northing: float, half_side: float = 10):
    """Build a small square polygon in WGS84 lon/lat centered on the given
    EPSG:25833 coordinate, using an exact round-trip reprojection rather than
    hand-approximated degree offsets."""
    center = gpd.GeoSeries([Point(easting, northing)], crs=DEFAULT_CRS).to_crs(
        "EPSG:4326"
    )
    lon, lat = center.iloc[0].x, center.iloc[0].y
    corner = gpd.GeoSeries(
        [Point(easting + half_side, northing + half_side)], crs=DEFAULT_CRS
    ).to_crs("EPSG:4326")
    dlon, dlat = abs(corner.iloc[0].x - lon), abs(corner.iloc[0].y - lat)

    return Polygon(
        [
            (lon - dlon, lat - dlat),
            (lon + dlon, lat - dlat),
            (lon + dlon, lat + dlat),
            (lon - dlon, lat + dlat),
        ]
    )


# --- _filter_building_geometries ---------------------------------------------


def test_filter_building_geometries_keeps_only_polygons(raw_osm_buildings_gdf):
    filtered = _filter_building_geometries(raw_osm_buildings_gdf)

    assert set(filtered.geometry.type) == {"Polygon", "MultiPolygon"}
    assert len(filtered) == 2


def test_filter_building_geometries_returns_empty_when_none_match():
    gdf = gpd.GeoDataFrame(
        geometry=[Point(0, 0), LineString([(0, 0), (1, 1)])],
    )

    filtered = _filter_building_geometries(gdf)

    assert len(filtered) == 0


def test_filter_building_geometries_keeps_all_polygon_input():
    gdf = gpd.GeoDataFrame(
        geometry=[box(0, 0, 1, 1), MultiPolygon([box(2, 2, 3, 3)])],
    )

    filtered = _filter_building_geometries(gdf)

    assert len(filtered) == 2


# --- get_osm_buildings ---------------------------------------------------------


def test_get_osm_buildings_rejects_invalid_districts_without_calling_osm(
    buildings_gdf,
):
    invalid_districts = buildings_gdf.rename(columns={"bydel": "not_bydel"})

    with patch("urbanmobility.buildings.processing.ox.features_from_place") as mock_ox:
        with pytest.raises(KeyError):
            get_osm_buildings(invalid_districts)

    mock_ox.assert_not_called()


def test_get_osm_buildings_defaults_to_building_tag(districts_gdf):
    empty_response = gpd.GeoDataFrame(geometry=[])

    with patch(
        "urbanmobility.buildings.processing.ox.features_from_place",
        return_value=empty_response,
    ) as mock_ox:
        get_osm_buildings(districts_gdf)

    _, kwargs = mock_ox.call_args
    assert kwargs["tags"] == {"building": True}


def test_get_osm_buildings_passes_through_custom_tags(districts_gdf):
    empty_response = gpd.GeoDataFrame(geometry=[])
    custom_tags = {"building": "residential"}

    with patch(
        "urbanmobility.buildings.processing.ox.features_from_place",
        return_value=empty_response,
    ) as mock_ox:
        get_osm_buildings(districts_gdf, tags=custom_tags)

    _, kwargs = mock_ox.call_args
    assert kwargs["tags"] == custom_tags


def test_get_osm_buildings_filters_mixed_geometry_and_assigns_districts(
    districts_gdf,
):
    building_in_a = _reprojected_wgs84_square(597500, 6643500)
    stray_point = (
        gpd.GeoSeries([Point(597500, 6643500)], crs=DEFAULT_CRS)
        .to_crs("EPSG:4326")
        .iloc[0]
    )

    mock_response = gpd.GeoDataFrame(
        {"element": ["polygon", "point"]},
        geometry=[building_in_a, stray_point],
    )

    with patch(
        "urbanmobility.buildings.processing.ox.features_from_place",
        return_value=mock_response,
    ):
        result = get_osm_buildings(districts_gdf)

    assert len(result) == 1
    assert result.iloc[0]["bydel"] == "A"


def test_get_osm_buildings_assumes_wgs84_when_crs_missing(districts_gdf):
    building_in_a = _reprojected_wgs84_square(597500, 6643500)
    mock_response = gpd.GeoDataFrame(geometry=[building_in_a])
    assert mock_response.crs is None

    with patch(
        "urbanmobility.buildings.processing.ox.features_from_place",
        return_value=mock_response,
    ):
        result = get_osm_buildings(districts_gdf)

    assert str(result.crs).upper() == DEFAULT_CRS.upper()


def test_get_osm_buildings_leaves_district_col_missing_for_buildings_outside_all_districts(
    districts_gdf,
):
    building_outside = _reprojected_wgs84_square(610000, 6650000)
    mock_response = gpd.GeoDataFrame(geometry=[building_outside])

    with patch(
        "urbanmobility.buildings.processing.ox.features_from_place",
        return_value=mock_response,
    ):
        result = get_osm_buildings(districts_gdf)

    assert len(result) == 1
    assert pd.isna(result.iloc[0]["bydel"])
