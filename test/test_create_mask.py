import pytest
import os
from lidro.rasters.create_mask_raster import CreateMask
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin

las_file_test = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
las_file= "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
output_tif = "./tmp/Semis_2021_0830_6291_LA93_IGN69_size_5.tif"


@pytest.fixture
def create_raster_instance():
    # Create instance from "CreateRatser" for the tests
    tile_size = 1000
    pixel_size = 1
    spatial_ref = 'EPSG:2154'
    no_data_value = -9999
    return CreateMask(
        tile_size=tile_size,
        pixel_size=pixel_size,
        spatial_ref=spatial_ref,
        no_data_value=no_data_value,
    )

def setup_module(module):
    os.makedirs('tmp', exist_ok = True)

def test_input_exist():
    assert Path(las_file).exists()

def test_check_type(create_raster_instance):
    array = create_raster_instance.create_mask(las_file_test, classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ])
    assert isinstance(array, np.ndarray) is True

def test_save_output(create_raster_instance):
    array = create_raster_instance.create_mask(las_file, classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ])
    
    # Transform
    transform = from_origin(830000, 6291000, 1, 1)

    # Save the result
    with rasterio.open(output_tif, 'w', driver='GTiff', height=array.shape[0], width=array.shape[1], count=1, dtype=rasterio.uint8, crs='EPSG:2154', transform=transform) as dst:
        dst.write(array, 1)

    assert Path(output_tif).exists()