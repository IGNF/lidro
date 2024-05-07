import os
import shutil
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Polygon

from lidro.merge_mask_hydro.vectors.merge_vector import merge_geom

TMP_PATH = Path("./tmp/merge_mask_hydro/vectors/merge_mask_hydro")

input_folder = "./data/mask_hydro/"
output = Path("./tmp/merge_mask_hydro/vectors/merge_mask_hydro/MaskHydro_merge.geojson")
output_main = "./data/merge_mask_hydro/MaskHydro_merge.geojson"


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_create_hydro_vector_mask_default():
    # Parameters
    min_water_area = 150
    buffer_positive = 0.5
    buffer_negative = -1.5
    tolerance = 1
    crs = CRS.from_epsg(2154)

    merge_geom(input_folder, TMP_PATH, crs, min_water_area, buffer_positive, buffer_negative, tolerance)
    assert Path(output).exists()

    gdf = gpd.read_file(output)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical
    assert all(isinstance(geom, Polygon) for geom in gdf.geometry)  # All geometry should Polygons

    expected_number_of_geometries = 1
    assert len(gdf) == expected_number_of_geometries  # One geometry
