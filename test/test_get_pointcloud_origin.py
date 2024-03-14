import laspy
import numpy as np

from lidro.utils.get_pointcloud_origin import get_pointcloud_origin

LAS_FILE = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
LAS = laspy.read(LAS_FILE)
INPUT_POINTS = np.vstack((LAS.x, LAS.y, LAS.z)).transpose()
EXPECTED_ORIGIN = (706000, 6627000)


def test_get_pointcloud_origin_return_origin():
    origin_x, origin_y = get_pointcloud_origin(points=INPUT_POINTS, tile_size=1000)
    assert (origin_x, origin_y) == EXPECTED_ORIGIN
