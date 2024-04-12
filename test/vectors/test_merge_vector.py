import os
import shutil
from pathlib import Path

from lidro.vectors.merge_vector import merge_geom

INPUT_FOLDER = Path("./tmp/main/main_lidro_default")
TMP_PATH = Path("./tmp/vectors/merge_vector")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_merge_mask_default():
    output = "tmp/vectors/merge_vector/MaskHydro_merge.geojson"
    merge_geom(INPUT_FOLDER, TMP_PATH, "epsg:2154")

    assert Path(output).exists()
