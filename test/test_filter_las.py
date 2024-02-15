

import pytest
from lidro.pointcloud.filter_las import filter_pointcloud
import numpy as  np
from pathlib import Path

las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"


def test_input_exist():
    assert Path(las_file).exists()

def test_return_format_okay():
    output = filter_pointcloud(las_file, [2, 3, 4, 5])
    assert isinstance(output, np.ndarray) is True

def test_return_format_classes_error():
    with pytest.raises(TypeError):
        assert filter_pointcloud(las_file, 2)


