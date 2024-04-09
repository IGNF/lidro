import os
import shutil
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from lidro.rasters.create_mask_raster import create_occupancy_map, detect_hydro_by_tile

TMP_PATH = Path("./tmp/rasters/create_mask_raster")

LAS_FILE = "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"


tile_size = 1000
pixel_size = 1


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_create_occupancy_map_default():
    # test on points that are on a tile with origin = (10, 10)
    # if we hav tile_size = 10, this means that the tile extent is:
    # x: [10, 20]
    # y: [0, 10]
    # points are stored as x, y, w
    points = np.array([[10.5, 1.5, 0], [10.5, 2.5, 1], [10.5, 1.5, 1]])
    expected_occupancy = np.zeros([10, 10])
    expected_occupancy[-2, 0] = 1  # numpy array is stored as y, x and upper row first (unlike occupancy map)
    expected_occupancy[-3, 0] = 1
    print(expected_occupancy)
    occupancy_map = create_occupancy_map(points, tile_size=10, pixel_size=1, origin=(10, 10))
    print(occupancy_map)
    assert np.all(occupancy_map == expected_occupancy)


@pytest.mark.returnfile
def test_detect_hydro_by_tile_return_file():
    output_tif = TMP_PATH / "Semis_2021_0830_6291_LA93_IGN69_size.tif"
    array, origin = detect_hydro_by_tile(LAS_FILE, tile_size, pixel_size, classes=[0, 1, 2, 3, 4, 5, 6, 17, 66])

    assert isinstance(array, np.ndarray) is True
    assert list(array.shape) == [tile_size / pixel_size] * 2
    assert np.any(array)  # Check that not all values are 0
    assert not np.all(array)  # Check that not all values are 1

    # Transform
    transform = from_origin(origin[0], origin[1], 1, 1)

    # Save the result
    with rasterio.open(
        output_tif,
        "w",
        driver="GTiff",
        height=array.shape[0],
        width=array.shape[1],
        count=1,
        dtype=rasterio.uint8,
        crs="EPSG:2154",
        transform=transform,
    ) as dst:
        dst.write(array, 1)

    assert Path(output_tif).exists()
