import os
import shutil
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import Polygon

from lidro.create_mask_hydro.vectors.convert_to_vector import create_hydro_vector_mask

TMP_PATH = Path("./tmp/create_mask_hydro/vectors/convert_to_vector")

las_file = "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
output = "./tmp/create_mask_hydro/vectors/convert_to_vector/MaskHydro_Semis_2021_0830_6291_LA93_IGN69.GeoJSON"



def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_create_hydro_vector_mask_default():
    # Parameters
    pixel_size = 1
    tile_size = 1000
    classes = [0, 1, 2, 3, 4, 5, 6, 17, 66]
    crs = CRS.from_epsg(2154)
    dilatation_size = 3

    create_hydro_vector_mask(las_file, output, pixel_size, tile_size, classes, crs, dilatation_size)
    assert Path(output).exists()

def test_check_structure_default():
    # Output
    with open(output, "r") as f:
        geojson_data = json.load(f)
    
    with open(output_main, "r") as f:
        geojson_data_main = json.load(f)

        # CHECK STRUCTURE
        assert "type" in geojson_data
        assert geojson_data["type"] == "FeatureCollection"
        assert "features" in geojson_data
        assert isinstance(geojson_data["features"], list)

       # CHECK POLYGON
        for feature in geojson_data["features"]:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]

        for feature in geojson_data_main["features"]:
            geometry_main = feature["geometry"]
            coordinates_main = geometry_main["coordinates"]
        
        assert coordinates[0] == coordinates_main[0]
   

