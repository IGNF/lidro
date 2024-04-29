import os
import shutil
from pathlib import Path

import numpy as np

from lidro.create_mask_hydro.pointcloud.filter_las import filter_pointcloud

TMP_PATH = Path("./tmp/create_mask_hydro/pointcloud/filter_las")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_filter_pointcloud_default():
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

    output = filter_pointcloud(array_points, [2, 3, 4])
    assert isinstance(output, np.ndarray) is True
    assert np.all(np.isin(output[:, -1], [2, 3, 4]))
    assert output.shape[0] == 11
