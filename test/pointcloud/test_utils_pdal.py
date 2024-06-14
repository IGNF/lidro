import numpy as np

from lidro.create_virtual_point.pointcloud.utils_pdal import (
    get_bounds_from_las,
    read_las_file,
)

LAS_FILE = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"

# Expected : ([minx,maxx],[miny,maxy])
BoundsExpected_FILE = ([706044.94, 706292.25], [6626159, 6626324])


def test_read_las_file():
    pts = read_las_file(LAS_FILE)
    assert isinstance(pts, np.ndarray)  # type is array


def test_get_bounds_from_las():
    bounds = get_bounds_from_las(LAS_FILE)

    assert isinstance(bounds, tuple)
    assert bounds == BoundsExpected_FILE
