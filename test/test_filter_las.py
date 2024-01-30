import pytest
from lidro.filter.filter_las import read_point_cloud
import numpy as  np
from pathlib import Path

las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"


def test_input_exist():
    assert Path(las_file).exists()

def test_return_format_okay():
    output = read_point_cloud(las_file, [2], 'EPSG:2154')
    assert isinstance(output, np.ndarray) is True

def test_return_format_classes_error():
    with pytest.raises(TypeError):
        assert read_point_cloud(las_file, 2, 'EPSG:2154')

def test_return_format_spatial_error():
    with pytest.raises(TypeError):
        assert read_point_cloud(las_file, [2], 2154)
