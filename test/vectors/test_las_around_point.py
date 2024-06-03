import os
import shutil
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.las_around_point import filter_las_around_point

TMP_PATH = Path("./tmp/create_virtual_point/vectors/las_around_point")

file_skeleton = "./data/skeleton_hydro/Skeleton_Hydro.geojson"
file_mask = "./data/merge_mask_hydro/MaskHydro_merge.geojson"
file_lidar = "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
output = Path("./tmp/create_virtual_point/vectors/las_around_point/Points.geojson")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_las_around_point_default():
    # Parameters
    distance_meters = 10
    k = 6
    classes = "[2:2]"
    crs = CRS.from_epsg(2154)

    result = filter_las_around_point(file_skeleton, file_mask, file_lidar, distance_meters, k, classes, crs)

    # Convert results to GeoDataFrame
    result_gdf = gpd.GeoDataFrame(result)
    result_gdf.set_crs(crs, inplace=True)
    # Save to GeoJSON
    result_gdf.to_file(output, driver="GeoJSON")

    gdf = gpd.read_file(output)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, Point) for geom in gdf.geometry)  # All geometry should Points
