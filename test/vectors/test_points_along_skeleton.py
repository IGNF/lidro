import os
import shutil
from pathlib import Path

import geopandas as gpd
import numpy as np
from pyproj import CRS
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.points_along_skeleton import (
    generate_points_along_skeleton,
)

TMP_PATH = Path("./tmp/create_point_virtual/vectors/points_along_skeleton")

input_folder = "./data/skeleton_hydro/"
file = "Skeleton_Hydro.geojson"
output = Path("./tmp/create_point_virtual/vectors/points_along_skeleton/Points.geojson")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_points_along_skeleton_default():
    # Parameters
    distance_meters = 2
    crs = CRS.from_epsg(2154)

    result = generate_points_along_skeleton(input_folder, file, distance_meters, crs)

    # Save the result to GeoJSON
    result.to_file(output, driver="GeoJSON", crs=crs)

    assert Path(output).exists()

    gdf = gpd.read_file(output)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, Point) for geom in gdf.geometry)  # All geometry should Points

    # Calculate distances between consecutive points and check they match the expected distance
    distances = [round(gdf.geometry[i].distance(gdf.geometry[i + 1]), 2) for i in range(len(gdf.geometry) - 1)]

    # print("Distances:", distances)
    # Assert that distances from 10 first points are close to the specified distance with a tolerance of 0.2 meters
    assert np.allclose(distances[1:10], 2.0, atol=0.2)  # 0.2 meter tolerance for calculation errors
