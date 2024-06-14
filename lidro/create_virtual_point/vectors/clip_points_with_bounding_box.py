# -*- coding: utf-8 -*-
""" Clip Skeleton points by tile (pointcloud)
"""
from typing import List

import geopandas as gpd
from shapely.geometry import Point, box


def clip_points_with_box(points: List, bbox: tuple) -> gpd.GeoDataFrame:
    """Clip skeleton points by tile (bounding box)

    Args:
        points (List): Points every 2 meters (by default) along skeleton hydro
        bbox (tuple): bounding box from tile (pointcloud)

    Returns:
       gpd.GeoDataframe : Points every 2 meters (by default) along skeleton hydro by tile
    """
    # Extract the bounding box limits
    xmin = bbox[0][0]
    xmax = bbox[0][1]
    ymin = bbox[1][0]
    ymax = bbox[1][1]

    # Create a GeoDataFrame from the points
    gdf_points = gpd.GeoDataFrame(geometry=[Point(point) for point in points])
    # Create a polygon representing the bounding box
    bounding_box = box(xmin, ymin, xmax, ymax)

    # Clip points using the bounding box
    clipped_points = gdf_points[gdf_points.within(bounding_box)]

    return clipped_points
