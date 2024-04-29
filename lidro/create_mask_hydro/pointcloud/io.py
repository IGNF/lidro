# -*- coding: utf-8 -*-
""" extract coordinates the original tiles without buffer """
import numpy as np


def get_pointcloud_origin(points: np.array, tile_size: int = 1000, buffer_size: float = 0):
    # Extract coordinates xmin, xmax, ymin and ymax of the original tile without buffer
    x_min, y_min = np.min(points[:, :2], axis=0) + buffer_size
    x_max, y_max = np.max(points[:, :2], axis=0) - buffer_size

    # Calculate the difference Xmin and Xmax, then Ymin and Ymax
    diff_x = x_min - x_max
    diff_y = y_min - y_max
    # Check [x_min - x_max] == amplitude and [y_min - y_max] == amplitude
    if abs(diff_x) <= tile_size and abs(diff_y) <= tile_size:
        origin_x = np.floor(x_min / tile_size) * tile_size  # round low
        origin_y = np.ceil(y_max / tile_size) * tile_size  # round top
        return origin_x, origin_y
    else:
        raise ValueError(f"Extents (diff_x={diff_x} and diff_y={diff_y}) is bigger than tile_size ({tile_size}).")
