import os
import shutil
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.extract_points_around_skeleton import (
    extract_points_around_skeleton_points_one_tile,
)

TMP_PATH = Path("./tmp/create_virtual_point/vectors/extract_points_around_skeleton")
INPUT_DIR = Path("./data/")
MASK_HYDRO = "./data/merge_mask_hydro/MaskHydro_merge.geojson"
POINTS_SKELETON = "./data/skeleton_hydro/points_along_skeleton_small.geojson"
OUTPUT_GEOJSON = TMP_PATH / "Semis_2021_0830_6291_LA93_IGN69_points_skeleton.geojson"


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_extract_points_around_skeleton_default():
    # Parameters
    crs = CRS.from_epsg(2154)
    classes = [2]  # Example classes
    k = 3  # Example k value

    # Mask Hydro with buffer
    mask_hydro_buffered = "MULTIPOLYGON (((829969.0856167737 6292032.553442742,\
        830452.9506643447 6292032.553442742, \
        830498.1716968281 6291675.307286125, \
        830624.7905877812 6291073.867554097, \
        830783.0642014727 6290675.922468244, \
        830972.9925379024 6290400.074170096, \
        831045.3461898757 6290228.23424666, \
        831036.3019833791 6289952.385948512, \
        830783.0642014727 6289947.863845264, \
        830371.5528058748 6290599.046713023, \
        830055.005578492 6290947.248663144, \
        829919.3424810421 6291399.458987976, \
        829969.0856167737 6292032.553442742)))"

    # Execute the function
    extract_points_around_skeleton_points_one_tile(
        "Semis_2021_0830_6291_LA93_IGN69.laz",
        INPUT_DIR,
        TMP_PATH,
        mask_hydro_buffered,
        gpd.read_file(POINTS_SKELETON),
        crs,
        classes,
        k,
    )

    # Verify that the output file exists
    assert OUTPUT_GEOJSON.exists()

    # Load the output GeoJSON
    gdf = gpd.read_file(OUTPUT_GEOJSON)

    # Assertions to check the integrity of the output
    assert not gdf.empty, "GeoDataFrame shouldn't be empty"
    assert gdf.crs.to_string() == crs.to_string(), "CRS should match the specified CRS"
    assert all(isinstance(geom, Point) for geom in gdf.geometry), "All geometries should be Points"
