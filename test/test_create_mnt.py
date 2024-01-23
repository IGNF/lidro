import pytest
import os
from lidro.tasks.create_mnt import CreateRaster
import rasterio
from pathlib import Path

input_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
raster_file = "./tmp/test_mnt_0706_6627_LAMB93_IGN69_50CM_TIN.tif"

def setup_module(module):
    os.makedirs('tmp', exist_ok = True)

@pytest.fixture
def create_raster_instance():
    # Create instance from "CreateRatser" for the tests
    nb_pixels = [2000, 2000]
    origin = [706000.0, 6627000.0]
    pixel_size = 0.5
    spatial_ref = 'EPSG:2154'
    no_data_value = -9999
    tile_width = 1000
    tile_coord_scale = 1000
    classes = [2, 66]
    return CreateRaster(
        nb_pixels=nb_pixels,
        origin=origin,
        pixel_size=pixel_size,
        spatial_ref=spatial_ref,
        no_data_value=no_data_value,
        tile_width=tile_width,
        tile_coord_scale=tile_coord_scale,
        classes=classes
    )

def test_unexisting_input_las(create_raster_instance):
    with pytest.raises(RuntimeError):
        create_raster_instance.execute_pdal_tin("./test_unuexisting.las", "")

def test_execute_pdal_tin(create_raster_instance):
    create_raster_instance.execute_pdal_tin(input_file, raster_file)
    # Check if raster exists
    assert os.path.isfile(raster_file)

def test_raster_resolution():
     with rasterio.open(raster_file) as src:
        if src is not None:
            resolution = src.res
            assert resolution == (0.5, 0.5)

def test_raster_band():
     with rasterio.open(raster_file) as src:
        if src is not None:
            num_bands = src.count
            assert num_bands == 1

def test_raster_z_nodata():
     with rasterio.open(raster_file) as src:
        raster = src.read(1)
        # check that Z have a nodata value
        assert (raster == -9999).any()

def test_raster_z_error():
     with rasterio.open(raster_file) as src:
        raster = src.read(1)
        print(raster)
        with pytest.raises(ValueError):
            # check that Z have not a negative value
            assert (-9999 < raster < 0).any()
