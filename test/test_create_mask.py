import pytest
import os
from lidro.rasters.create_mask_raster import create_mask
from pathlib import Path
import numpy as np

las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"

def setup_module(module):
    os.makedirs('tmp', exist_ok = True)

def test_input_exist():
    assert Path(las_file).exists()

def test_create_mask_raster():
    output = create_mask(las_file, pixel_size = 0.5, nb_pixels = (1000, 1000), classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ])
    assert isinstance(output, np.ndarray) is True