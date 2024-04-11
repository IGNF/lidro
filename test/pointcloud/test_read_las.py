import os
import shutil
from pathlib import Path

import numpy as np
from pyproj import CRS

from lidro.pointcloud.read_las import read_pointcloud

TMP_PATH = Path("./tmp/pointcloud/io")

LAS_FILE = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_read_pointcloud_return_format_okay():
    output, crs = read_pointcloud(LAS_FILE)

    assert isinstance(output, np.ndarray) is True

    assert CRS.from_user_input("EPSG:2154")
