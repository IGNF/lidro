import os
import shutil
from pathlib import Path

import pandas as pd
from pyproj import CRS

from lidro.create_virtual_point.vectors.merge_skeleton_by_mask import (
    merge_skeleton_by_mask,
)

TMP_PATH = Path("./tmp/virtual_points/vectors/merge_skeleton_by_mask")

mask = Path("./data/merge_mask_hydro/MaskHydro_merge.geojson")
skeleton = Path("./data/skeleton_hydro/Skeleton_Hydro.geojson")
output = Path("./tmp/virtual_points/vectors/merge_skeleton_by_mask/merge_skeleton_by_mask.geojson")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_merge_skeleton_by_mask_default():
    # Parameters
    crs = CRS.from_epsg(2154)

    result = merge_skeleton_by_mask(skeleton, mask, TMP_PATH, crs)

    # Check if the result is a DataFrame
    assert isinstance(result, pd.DataFrame), "Result is not a DataFrame"

    # Check if the necessary columns are present
    assert "geometry_skeleton" in result.columns, "Missing 'geometry_skeleton' column"
    assert "geometry_mask" in result.columns, "Missing 'geometry_mask' column"
