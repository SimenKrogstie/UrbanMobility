import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from urbanmobility.buildings.validation import (
    validate_geodataframe,
    validate_columns,
    validate_districts,
    validate_building_data,
    validate_indicators,
    validate_districts_exist,
    validate_building_plot_data,
)
from urbanmobility.config import DEFAULT_CRS


# --- validate_geodataframe ---------------------------------------------------


def test_validate_geodataframe_rejects_non_geodataframe():
    with pytest.raises(TypeError):
        validate_geodataframe(pd.DataFrame({"a": [1]}), "gdf")  # type: ignore[arg-type]


def test_validate_geodataframe_rejects_missing_geometry_column():
    gdf = gpd.GeoDataFrame({"bydel": ["A"]})
    with pytest.raises(ValueError):
        validate_geodataframe(gdf, "gdf")


def test_validate_geodataframe_rejects_empty_geometry(empty_geometry_gdf):
    with pytest.raises(ValueError):
        validate_geodataframe(empty_geometry_gdf, "gdf")


def test_validate_geodataframe_rejects_invalid_geometry(invalid_geometry_gdf):
    with pytest.raises(ValueError):
        validate_geodataframe(invalid_geometry_gdf, "gdf")


def test_validate_geodataframe_accepts_valid_input(districts_gdf):
    validate_geodataframe(districts_gdf, "gdf")


# --- validate_columns ---------------------------------------------------------


def test_validate_columns_reports_single_missing_column(districts_gdf):
    with pytest.raises(KeyError, match="population"):
        validate_columns(districts_gdf, ["bydel", "population"], "gdf")


def test_validate_columns_reports_all_missing_columns(districts_gdf):
    with pytest.raises(KeyError) as exc_info:
        validate_columns(districts_gdf, ["population", "area"], "gdf")

    assert "population" in str(exc_info.value)
    assert "area" in str(exc_info.value)


def test_validate_columns_passes_when_all_present(districts_gdf):
    validate_columns(districts_gdf, ["bydel", "geometry"], "gdf")


def test_validate_columns_passes_for_empty_column_list(districts_gdf):
    validate_columns(districts_gdf, [], "gdf")


# --- validate_districts --------------------------------------------------------


def test_validate_districts_rejects_invalid_geometry(invalid_geometry_gdf):
    with pytest.raises(ValueError):
        validate_districts(invalid_geometry_gdf, "bydel")


def test_validate_districts_rejects_missing_district_col(districts_gdf):
    with pytest.raises(KeyError):
        validate_districts(districts_gdf, "missing_col")


def test_validate_districts_passes_for_valid_input(districts_gdf):
    validate_districts(districts_gdf, "bydel")


# --- validate_building_data -----------------------------------------------------


def test_validate_building_data_rejects_non_geodataframe_buildings(districts_gdf):
    with pytest.raises(TypeError):
        validate_building_data(
            pd.DataFrame({"bydel": ["A"]}),  # type: ignore[arg-type]
            districts_gdf,
            "bydel",
        )


def test_validate_building_data_rejects_invalid_district_geometry(
    buildings_gdf, invalid_geometry_gdf
):
    with pytest.raises(ValueError):
        validate_building_data(buildings_gdf, invalid_geometry_gdf, "bydel")


def test_validate_building_data_rejects_missing_district_col_in_buildings(
    districts_gdf,
):
    buildings = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)], crs=DEFAULT_CRS)
    with pytest.raises(KeyError):
        validate_building_data(buildings, districts_gdf, "bydel")


def test_validate_building_data_rejects_missing_district_col_in_districts(
    buildings_gdf, districts_gdf
):
    districts = districts_gdf.drop(columns=["bydel"])
    with pytest.raises(KeyError):
        validate_building_data(buildings_gdf, districts, "bydel")


def test_validate_building_data_passes_for_matched_valid_input(
    buildings_gdf, districts_gdf
):
    validate_building_data(buildings_gdf, districts_gdf, "bydel")


# --- validate_indicators -----------------------------------------------------


def test_validate_indicators_reports_missing_indicator_columns(districts_gdf):
    with pytest.raises(KeyError, match="density"):
        validate_indicators(districts_gdf, ["density"])


def test_validate_indicators_passes_when_all_present(districts_gdf):
    validate_indicators(districts_gdf, ["bydel"])


# --- validate_districts_exist -------------------------------------------------


def test_validate_districts_exist_rejects_absent_district(districts_gdf):
    with pytest.raises(KeyError, match="C"):
        validate_districts_exist(districts_gdf, ["A", "C"], "bydel")


def test_validate_districts_exist_is_case_sensitive(districts_gdf):
    with pytest.raises(KeyError):
        validate_districts_exist(districts_gdf, ["a"], "bydel")


def test_validate_districts_exist_passes_when_present(districts_gdf):
    validate_districts_exist(districts_gdf, ["A", "B"], "bydel")


def test_validate_districts_exist_checks_index_when_district_col_is_the_index(
    districts_gdf,
):
    indexed = districts_gdf.set_index("bydel")

    validate_districts_exist(indexed, ["A", "B"], "bydel")

    with pytest.raises(KeyError):
        validate_districts_exist(indexed, ["C"], "bydel")


# --- validate_building_plot_data ------------------------------------------------


def test_validate_building_plot_data_rejects_missing_type_col(buildings_gdf):
    with pytest.raises(KeyError):
        validate_building_plot_data(buildings_gdf, "bydel", "building")


def test_validate_building_plot_data_rejects_missing_district_col(
    building_types_gdf,
):
    gdf = building_types_gdf.drop(columns=["bydel"])
    with pytest.raises(KeyError):
        validate_building_plot_data(gdf, "bydel", "building")


def test_validate_building_plot_data_passes_for_valid_input(building_types_gdf):
    validate_building_plot_data(building_types_gdf, "bydel", "building")
