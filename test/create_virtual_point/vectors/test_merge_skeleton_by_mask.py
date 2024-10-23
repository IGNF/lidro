import os
import shutil
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from pyproj import CRS
from shapely import LineString, Polygon

from lidro.create_virtual_point.vectors.merge_skeleton_by_mask import (
    combine_skeletons,
    merge_skeleton_by_mask,
)

TMP_PATH = Path("./tmp/virtual_points/vectors/merge_skeleton_by_mask")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


@pytest.mark.parametrize(
    "skeletons, hydro_masks, expected_out",
    [
        (
            [LineString([(0, 0), (1, 1)])],
            [Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])],
            gpd.GeoDataFrame({"index_right": [0], "geometry": [LineString([(0, 0), (1, 1)])], "index_mask": [0]}),
        ),  # simple case: one skeleton fully inside one hydro mask
        (
            [LineString([(0, 0), (2, 2)])],
            [Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])],
            gpd.GeoDataFrame({"index_right": [0], "geometry": [LineString([(0, 0), (1, 1)])], "index_mask": [0]}),
        ),  # one skeleton partly inside one hydro mask
        (
            [LineString([(0, 0), (0.5, 0.5)]), LineString([(1, 1), (0.5, 0.5)])],
            [Polygon([[0, 0], [0, 1], [1, 1], [1, 0]])],
            gpd.GeoDataFrame(
                {"index_right": [0], "geometry": [LineString([(0, 0), (0.5, 0.5), (1, 1)])], "index_mask": [0]}
            ),
        ),  # 2 joint skeletons in 1 hydro masks
    ],
)
def test_combine_skeletons(skeletons, hydro_masks, expected_out):
    crs = CRS.from_epsg(2154)
    gdf_skeletons = gpd.GeoDataFrame(geometry=skeletons, crs=crs)
    gdf_hydro_masks = gpd.GeoDataFrame(geometry=hydro_masks, crs=crs)

    out = combine_skeletons(gdf_skeletons, gdf_hydro_masks, crs)
    assert out.equals(expected_out)


@pytest.mark.parametrize(
    "skeletons, hydro_masks",
    [
        (
            [LineString([(0, 0), (0.1, 0.1)]), LineString([(0.9, 0.9), (1, 1)])],
            [Polygon(shell=[(0, 0), (0, 1), (1, 1), (1, 0)])],
        ),  # disjoint skeleton
        (
            [LineString([(0, 0), (1, 1)])],
            [
                Polygon(
                    shell=[(0, 0), (0, 1), (1, 1), (1, 0)], holes=[[(0.4, 0.4), (0.6, 0.4), (0.6, 0.6), (0.4, 0.6)]]
                )
            ],
        ),  # one skeleton partly inside one hydro mask with a hole, will be cut into 2 parts which cannot join
    ],
)
def test_combine_skeletons_raise(skeletons, hydro_masks):
    crs = CRS.from_epsg(2154)
    gdf_skeletons = gpd.GeoDataFrame(geometry=skeletons, crs=crs)
    print(gdf_skeletons)
    gdf_hydro_masks = gpd.GeoDataFrame(geometry=hydro_masks, crs=crs)
    print(gdf_hydro_masks)

    with pytest.raises(ValueError):
        combine_skeletons(gdf_skeletons, gdf_hydro_masks, crs)


@pytest.mark.parametrize(
    "skeleton, mask",
    [
        (  # simple mono_branch skeleton (real case)
            Path("./data/OM_subset/skeleton/skeleton_hydro.geojson"),
            Path("./data/OM_subset/mask_hydro_merge/MaskHydro_merge.geojson"),
        ),
        (  # simple mono_branch skeleton going over an island
            Path("./data/OM_subset/skeleton//skeleton_hydro_over_island.geojson"),
            Path("./data/OM_subset/mask_hydro_merge/MaskHydro_merge.geojson"),
        ),
        (  # mono_branch skeleton with mutliple LineString
            # original skeleton code generated skeleton_hydro_fail_with_small_gap.geojson which failed
            # newer output should pass
            Path("./data/tile_0830_6291/skeleton/skeleton_hydro.geojson"),
            Path("./data/tile_0830_6291/mask_hydro_merge/MaskHydro_merge.geojson"),
        ),
    ],
)
def test_merge_skeleton_by_mask_default(skeleton, mask):
    # Parameters
    crs = CRS.from_epsg(2154)

    result = merge_skeleton_by_mask(skeleton, mask, TMP_PATH, crs)

    # Check if the result is a DataFrame
    assert isinstance(result, pd.DataFrame), "Result is not a DataFrame"

    # Check if the necessary columns are present
    assert "geometry_skeleton" in result.columns, "Missing 'geometry_skeleton' column"
    assert "geometry_mask" in result.columns, "Missing 'geometry_mask' column"


@pytest.mark.parametrize(
    "skeleton, mask",
    [
        (  # simple mono_branch skeleton, which in fact has 2 parts that are disjoint of around 1 mm
            Path("./data/tile_0830_6291/skeleton/skeleton_hydro_fail_with_small_gap.geojson"),
            Path("./data/tile_0830_6291/mask_hydro_merge/MaskHydro_merge.geojson"),
        ),
        (  # multi_branch skeleton (should not happen)
            Path("./data/tile_0830_6291/skeleton/skeleton_hydro_fail_with_multibranch.geojson"),
            Path("./data/tile_0830_6291/mask_hydro_merge/MaskHydro_merge.geojson"),
        ),
    ],
)
def test_merge_skeleton_by_mask_fail(skeleton, mask):
    # Parameters
    crs = CRS.from_epsg(2154)

    with pytest.raises(ValueError):
        merge_skeleton_by_mask(skeleton, mask, TMP_PATH, crs)
