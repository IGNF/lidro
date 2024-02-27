import pytest
import os

from lidro.rasters.create_mask_raster import detect_hydro_by_tile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

las_file_test = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
las_file= "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
output_tif = "./tmp/Semis_2021_0830_6291_LA93_IGN69_size.tif"

tile_size = 1000
pixel_size = 1


def setup_module(module):
    os.makedirs('tmp', exist_ok = True)

def test_input_exist():
    assert Path(las_file).exists()

def test_check_type():
    array = detect_hydro_by_tile(las_file_test, tile_size, pixel_size, classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ])
    assert isinstance(array, np.ndarray) is True

def test_save_output():
    array = detect_hydro_by_tile(las_file,  tile_size, pixel_size, classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ])
    
    # Transform
    transform = from_origin(830000, 6291000, 1, 1)

    # Save the result
    with rasterio.open(output_tif, 'w', driver='GTiff', height=array.shape[0], width=array.shape[1], count=1, dtype=rasterio.uint8, crs='EPSG:2154', transform=transform) as dst:
        dst.write(array, 1)

    assert Path(output_tif).exists()