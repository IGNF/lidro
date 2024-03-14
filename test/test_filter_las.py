import csv
import os
from pathlib import Path

import numpy as np

from lidro.pointcloud.filter_las import filter_pointcloud

array_points = np.array(
    [
        [6062.44, 6626308.5, 186.1, 2],
        [6062.44, 6626308.0, 186.1, 2],
        [6062.44, 6626306.5, 186.1, 2],
        [6062.44, 6626306.0, 186.12, 1],
        [6062.44, 6626306.0, 186.1, 1],
        [6062.5, 6626304.5, 186.22, 2],
        [6062.06, 6626309.0, 186.08, 2],
        [6062.06, 6626308.5, 186.1, 5],
        [6062.06, 6626308.5, 186.1, 5],
        [6062.06, 6626308.0, 186.1, 5],
        [6062.06, 6626307.5, 186.1, 5],
        [6062.13, 6626307.5, 186.12, 2],
        [6062.13, 6626307.0, 186.12, 2],
        [6062.06, 6626306.5, 186.1, 2],
        [6062.13, 6626305.5, 186.16, 2],
        [6062.19, 6626303.0, 186.26, 2],
        [6062.19, 6626301.5, 186.36, 2],
        [6062.19, 6626301.0, 186.36, 5],
    ]
)

csv_file = "./tmp/filter_las/pointcloud_filter.csv"


def setup_module(module):
    os.makedirs("tmp/filter_las", exist_ok=True)


def test_return_format_okay():
    output = filter_pointcloud(array_points, [2, 3, 4, 5])
    assert isinstance(output, np.ndarray) is True


def test_filter_pointcloud_save_output():
    array = filter_pointcloud(array_points, [0, 1, 2])

    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(array)

    assert Path(csv_file).exists()
