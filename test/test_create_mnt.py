import pytest
from lidro.tasks.create_mnt import CreateRaster
import rasterio
from pathlib import Path

raster_file = "./data/DTM/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST_50CM_TINlinear.tif"

def test_create_mnt_okay():
    assert Path(raster_file).exists()

def check_raster_resolution_50cm():
     with rasterio.open(raster_file) as src:
        if src is not None:
            resolution = src.res
            assert resolution == 0.5

def check_raster_band():
     with rasterio.open(raster_file) as src:
        if src is not None:
            num_bands = src.count
            assert num_bands == 1

def check_raster_z_nodata():
     with rasterio.open(raster_file) as src:
        raster = src.read(1)
        # check that Z have a nodata value
        assert (raster == -9999).any()

def check_raster_z_error():
     with rasterio.open(raster_file) as src:
        raster = src.read(1)
        with pytest.raises(ValueError):
            # check that Z have not a negative value
            assert (raster < 0).any()
