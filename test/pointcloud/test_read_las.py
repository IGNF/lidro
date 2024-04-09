import os
import shutil
from pathlib import Path

import laspy
import numpy as np

from lidro.pointcloud.io import get_pointcloud_origin
from lidro.pointcloud.read_las import read_pointcloud

TMP_PATH = Path("./tmp/pointcloud/io")

LAS_FILE = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"

def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_pointcloud_default():
    output, crs = read_pointcloud(LAS_FILE) # read pointcloud default

    assert isinstance(output, np.ndarray) is True

    assert (
        crs
        == 'PROJCS["RGF93 v1 / Lambert-93",GEOGCS["RGF93 v1",DATUM["Reseau_Geodesique_Francais_1993_v1",\
        SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],\
        AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
        UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4171"]],\
        PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],\
        PARAMETER["central_meridian",3],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],\
        PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],\
        UNIT["metre",1,AUTHORITY["EPSG","9001"]],\
        AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","2154"]]'
    )

    las = laspy.read(LAS_FILE)
    input_points = np.vstack((las.x, las.y, las.z)).transpose()
    expected_origin = (706000, 6627000)
    origin_x, origin_y = get_pointcloud_origin(points=input_points, tile_size=1000)
    assert (origin_x, origin_y) == expected_origin # get pointcloud origin

