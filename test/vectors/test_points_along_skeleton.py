import os
import shutil
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.points_along_skeleton import (
    generate_points_along_skeleton,
)

TMP_PATH = Path("./tmp/merge_mask_hydro/vectors/points_along_skeleton")

input_folder = "./data/skeleton_hydro/"
file = "Skeleton_Hydro.geojson"
output = Path("./tmp/merge_mask_hydro/vectors/points_along_skeleton/Points.geojson")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_create_hydro_vector_mask_default():
    # Parameters
    distance_meters = 2
    crs = CRS.from_epsg(2154)

    generate_points_along_skeleton(input_folder, TMP_PATH, file, distance_meters, crs)
    assert Path(output).exists()

    gdf = gpd.read_file(output)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, Point) for geom in gdf.geometry)  # All geometry should Points
