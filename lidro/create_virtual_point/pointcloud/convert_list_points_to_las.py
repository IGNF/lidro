# -*- coding: utf-8 -*-
""" this function convert GeoDataframe "virtual points" to LIDAR points
"""
import logging
import os
from typing import List

import laspy
import numpy as np
import pandas as pd
from shapely.geometry import Point


def list_points_to_las(virtual_points: List[Point], output_dir: str, crs: str, virtual_points_classes: int):
    """This function convert virtual points (List of virtuals points) to LIDAR points
       with classification for virtual points

    Args:
        virtual_points (List[Point]): A list containing virtuals points by hydrological entity
        output_dir (str): folder to output LAS
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        virtual_points_classes (int): The classification value to assign to those virtual points
    """
    # Combine all virtual points into a single GeoDataFrame
    grid_with_z = pd.concat(virtual_points, ignore_index=True)

    # Create a LAS file with laspy
    header = laspy.LasHeader(point_format=6, version="1.4")

    # Create a LAS file with laspy and add the VLR for CRS
    las = laspy.LasData(header)
    las.x = grid_with_z.geometry.x
    las.y = grid_with_z.geometry.y
    las.z = grid_with_z.geometry.z
    las.classification = virtual_points_classes * np.ones(len(grid_with_z.index))

    # Add CRS information to the VLR
    vlr = laspy.vlrs.known.WktCoordinateSystemVlr(crs.to_wkt())
    las.vlrs.append(vlr)

    # Save the LAS file
    output_laz = os.path.join(output_dir, "virtual_points.laz")
    with laspy.open(output_laz, mode="w", header=las.header, do_compress=True) as writer:
        writer.write_points(las.points)

    logging.info(f"Virtual points LAS file saved to {output_laz}")
