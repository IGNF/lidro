import json
import os
import shutil
from pathlib import Path

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
    crs = 'PROJCS["RGF93 v1 / Lambert-93",GEOGCS["RGF93 v1",DATUM["Reseau_Geodesique_Francais_1993_v1",\
            SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],\
            AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
            UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4171"]],\
            PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],\
            PARAMETER["central_meridian",3],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],\
            PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],\
            UNIT["metre",1,AUTHORITY["EPSG","9001"]],\
            AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","2154"]]'

    merge_geom(input_folder, TMP_PATH, crs, 150, 0.5, -1.5, 1)

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
