import pytest
from lidro.pointcloud.read_las import read_pointcloud
import numpy as  np
from pathlib import Path

las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"


def test_input_exist():
    assert Path(las_file).exists()

def test_return_format_okay():
    output = read_pointcloud(las_file)
    assert isinstance(output, np.ndarray) is True