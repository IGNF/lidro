import os
import shutil
from pathlib import Path

import geopandas as gpd
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

    result = gpd.GeoDataFrame(geometry=result, crs=crs)
    result.to_file(output, driver="GeoJSON", crs=crs)

    assert Path(output).exists()

    gdf = gpd.read_file(output)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, Point) for geom in gdf.geometry)  # All geometry should Points
