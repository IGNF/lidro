

import pytest
from lidro.pointcloud.filter_las import filter_pointcloud
import numpy as  np
from pathlib import Path
import csv

las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
csv_file = "./tmp/pointcloud_filter.csv"


def test_input_exist():
    assert Path(las_file).exists()

def test_return_format_okay():
    output = filter_pointcloud(las_file, [2, 3, 4, 5])
    assert isinstance(output, np.ndarray) is True

def test_return_format_classes_error():
    with pytest.raises(TypeError):
        assert filter_pointcloud(las_file, 2)

def test_save_filter_las():
    array = filter_pointcloud(las_file, [0, 1, 2])

    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(array)
    
    assert Path(csv_file).exists()
    
