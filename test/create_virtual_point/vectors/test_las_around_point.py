import os
import shutil
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import CRS
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.las_around_point import filter_las_around_point

TMP_PATH = Path("./tmp/create_virtual_point/vectors/las_around_point")

output = Path("./tmp/create_virtual_point/vectors/las_around_point/Points.geojson")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_las_around_point_default():
    # Parameters
    points_along_skeleton = [[830864.5181373736, 6290217.943739296], [830866.5957826116, 6290208.162525126]]

    points_clip = np.array(
        [
            [8.30822700e05, 6.29000133e06, 2.59000000e00],
            [8.30836950e05, 6.29000254e06, 2.47000000e00],
            [8.30837730e05, 6.29000379e06, 2.58000000e00],
            [8.30042740e05, 6.29041476e06, 3.09000000e00],
            [8.30033610e05, 6.29041739e06, 3.87000000e00],
            [8.30042180e05, 6.29041447e06, 3.10000000e00],
        ]
    )

    k = 6
    crs = CRS.from_epsg(2154)

    result = filter_las_around_point(points_along_skeleton, points_clip, k)

    # Create a pandas DataFrame from the flattened list
    df = pd.DataFrame(result)
    # Create a GeoDataFrame from the pandas DataFrame
    points_gdf = gpd.GeoDataFrame(df, geometry="geometry")
    points_gdf.set_crs(crs, inplace=True)

    assert not points_gdf.empty  # GeoDataFrame shouldn't empty
    assert points_gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, Point) for geom in points_gdf.geometry)  # All geometry should Points
