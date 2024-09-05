# -*- coding: utf-8 -*-
""" this function convert GeoDataframe "virtual points" to LIDAR points
"""
import logging
import os
from typing import List

import laspy
import numpy as np
from shapely.geometry import Point


def list_points_to_las(virtual_points: List[Point], output_dir: str, crs: str, virtual_points_class: int):
    """This function convert virtual points (List of virtuals points) to LIDAR points
       with classification for virtual points

    Args:
        virtual_points (List[Point]): A list containing virtuals points by hydrological entity
        output_dir (str): folder to output LAS
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        virtual_points_class (int): The classification value to assign to those virtual points
    """
    # Create a LAS file with laspy
    header = laspy.LasHeader(point_format=6, version="1.4")

    # Create a LAS file with laspy and add the VLR for CRS
    las = laspy.LasData(header)
    las.x = np.array([pt.x for pt in virtual_points])
    las.y = np.array([pt.y for pt in virtual_points])
    las.z = np.array([pt.y for pt in virtual_points])
    las.classification = virtual_points_class * np.ones([len(virtual_points)], dtype=np.uint8)

    # Add CRS information to the VLR
    vlr = laspy.vlrs.known.WktCoordinateSystemVlr(crs.to_wkt())
    las.vlrs.append(vlr)

    # Save the LAS file
    output_laz = os.path.join(output_dir, "virtual_points.laz")
    with laspy.open(output_laz, mode="w", header=las.header, do_compress=True) as writer:
        writer.write_points(las.points)

    logging.info(f"Virtual points LAS file saved to {output_laz}")
