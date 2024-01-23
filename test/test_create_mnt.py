import pytest
import os
from lidro.rasters.create_raster import CreateRaster
import rasterio
import numpy as np

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
        create_raster_instance.create_dtm("./test_unuexisting.las", "")

def test_create_dtm(create_raster_instance):
    create_raster_instance.create_dtm(input_file, raster_file)
    # Check if raster exists
    assert os.path.isfile(raster_file)

    with rasterio.open(raster_file) as src:
        assert src is not None
        assert src.res == (0.5, 0.5) # resolution
        assert src.count == 1 # num_band

        raster = src.read(1)

        # raster value must be positif, or no data (-9999)
        assert np.bitwise_or(raster > 0, raster == -9999).all()
