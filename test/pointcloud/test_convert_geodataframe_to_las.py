import os
import shutil
from pathlib import Path

import geopandas as gpd
import laspy
import numpy as np
import pyproj
from shapely.geometry import Point

# Import the function from your module
from lidro.create_virtual_point.pointcloud.convert_geodataframe_to_las import (
    geodataframe_to_las,
)

TMP_PATH = Path("./tmp/virtual_points/pointcloud/convert_geodataframe_to_las")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_geodataframe_to_las_default():
    # Create a sample GeoDataFrame with virtual points (EPSG:2154)
    points = gpd.GeoDataFrame(
        {
            "geometry": [
                Point(700000, 6600000, 10),
                Point(700001, 6600001, 15),
                Point(700002, 6600002, 20),
                Point(700010, 6600010, 25),
            ]
        },
        crs="EPSG:2154",
    )

    # Define the CRS
    crs = pyproj.CRS("EPSG:2154")

    # Call the function to test
    geodataframe_to_las([points], TMP_PATH, crs, 68)

    # Verify the output LAS file
    output_las = os.path.join(TMP_PATH, "virtual_points.laz")
    assert os.path.exists(output_las), "The output LAS file should exist"

    # Read the LAS file
    las = laspy.read(output_las)

    # Check that the coordinates match the input points
    expected_coords = np.array([[p.x, p.y, p.z] for p in points.geometry])
    actual_coords = np.vstack((las.x, las.y, las.z)).T
    np.testing.assert_array_almost_equal(
        actual_coords,
        expected_coords,
        decimal=5,
        err_msg="The coordinates in the LAS file do not match the input points",
    )

    # Check that the classification is 68 for all points
    expected_classification = np.full(len(points), 68, dtype=np.uint8)
    np.testing.assert_array_equal(
        las.classification,
        expected_classification,
        err_msg="The classification in the LAS file should be 68 for all points",
    )
