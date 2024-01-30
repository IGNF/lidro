import pytest
import os
from lidro.rasters.create_inverse_mask import create_inverse_mask
import rasterio
from pathlib import Path
import numpy as np

raster_file = "./tmp/test_mask_1_0706_6627_LAMB93_IGN69.tif"
inverse_file = "./tmp/test_mask_1_0706_6627_LAMB93_IGN69_inverse.tif"


def setup_module(module):
    os.makedirs('tmp', exist_ok = True)

def test_create_inverse_mask():
    create_inverse_mask(raster_file, inverse_file)
    # Check if raster exists
    assert os.path.isfile(inverse_file)

    with rasterio.open(inverse_file) as src:
        assert src is not None
        assert src.res == (0.5, 0.5) # resolution
        assert src.count == 1 # num_band

        raster = src.read(1)

        # raster value must be 0 or 1
        assert np.bitwise_or( raster == 1, raster == 0).all()
