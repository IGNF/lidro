import os
import shutil
from pathlib import Path

import numpy as np

from lidro.create_virtual_point.pointcloud.crop_las import (
    read_filter_and_crop_pointcloud,
)

TMP_PATH = Path("./tmp/create_virtual_point/pointcloud/crop_las")
LAS_FILE = "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_crop_pointcloud_default():
    classes = "[1:2]"

    geom = str(
        "MULTIPOLYGON (((830873.1249999998 6290475.625000002, \
            830610.0480769228 6290335.43269231, \
            830546.0096153843 6290405.528846156, \
            830803.0288461535 6290559.567307694, \
        830873.1249999998 6290475.625000002)), \
            ((830210.5288461539 6290861.298076924, \
            830205.0480769231 6290760.336538463, \
            830101.2019230769 6290759.471153848, \
            830103.2211538461 6290861.586538463, \
        830210.5288461539 6290861.298076924)))"
    )
    output = read_filter_and_crop_pointcloud(LAS_FILE, geom, classes)

    assert isinstance(output, np.ndarray) is True
    assert isinstance((output == 0).all(), bool) is False
