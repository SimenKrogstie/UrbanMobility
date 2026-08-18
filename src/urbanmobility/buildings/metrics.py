"""Mathematical calculations only"""

import geopandas as gpd
import pandas as pd
from ..config import (
    AREA_M2,
    AREA_KM2,
    BUILDING_COUNT,
    BUILDING_AREA,
    BUILDING_DENSITY,
    BUILT_AREA_PERCENT,
    AVG_BUILDING_AREA,
)


def aggregate_building_statistics(
    buildings: gpd.GeoDataFrame,
    district_col: str,
) -> pd.DataFrame:

    buildings[BUILDING_AREA] = buildings.geometry.area

    return (
        buildings.groupby(district_col)
        .agg(
            **{
                BUILDING_COUNT: ("geometry", "size"),
                BUILDING_AREA: (BUILDING_AREA, "sum"),
            }
        )
        .reset_index()
    )


def add_building_metrics(
    districts: pd.DataFrame,
) -> pd.DataFrame:

    districts[AREA_M2] = districts.geometry.area
    districts[AREA_KM2] = districts[AREA_M2] / 1_000_000

    districts[BUILDING_DENSITY] = districts[BUILDING_COUNT] / districts[AREA_KM2]

    districts[BUILT_AREA_PERCENT] = districts[BUILDING_AREA] / districts[AREA_M2] * 100

    districts[AVG_BUILDING_AREA] = (
        districts[BUILDING_AREA].div(districts[BUILDING_COUNT]).fillna(0)
    )

    return districts
