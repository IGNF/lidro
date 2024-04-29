import json
import os
import shutil
from pathlib import Path

from lidro.create_mask_hydro.vectors.convert_to_vector import create_hydro_vector_mask

TMP_PATH = Path("./tmp/create_mask_hydro/vectors/convert_to_vector")

las_file = "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
output = "./tmp/create_mask_hydro/vectors/convert_to_vector/MaskHydro_Semis_2021_0830_6291_LA93_IGN69.GeoJSON"
output_main = "./tmp/create_mask_hydro/main/main_lidro_default/MaskHydro_Semis_2021_0830_6291_LA93_IGN69.GeoJSON"


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_create_hydro_vector_mask_default():
    crs = 'PROJCS["RGF93 v1 / Lambert-93",GEOGCS["RGF93 v1",DATUM["Reseau_Geodesique_Francais_1993_v1",\
            SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],\
            AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
            UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4171"]],\
            PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],\
            PARAMETER["central_meridian",3],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],\
            PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],\
            UNIT["metre",1,AUTHORITY["EPSG","9001"]],\
            AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","2154"]]'

    create_hydro_vector_mask(las_file, output, 1, 1000, [0, 1, 2, 3, 4, 5, 6, 17, 66], crs, 3)

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
