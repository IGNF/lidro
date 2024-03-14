import os
import shutil
from pathlib import Path

import laspy
import numpy as np

from lidro.pointcloud.io import get_pointcloud_origin

TMP_PATH = Path("./tmp/pointcloud/io")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_get_pointcloud_origin_default():
    las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
    las = laspy.read(las_file)
    input_points = np.vstack((las.x, las.y, las.z)).transpose()
    expected_origin = (706000, 6627000)
    origin_x, origin_y = get_pointcloud_origin(points=input_points, tile_size=1000)
    assert (origin_x, origin_y) == expected_origin
