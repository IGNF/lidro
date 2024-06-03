# -*- coding: utf-8 -*-
""" Extract a Z elevation value every N meters along the hydrographic skeleton
"""
from typing import List

import geopandas as gpd
import numpy as np
from shapely.geometry import CAP_STYLE, Point

from lidro.create_virtual_point.pointcloud.crop_las import crop_pointcloud_by_points
from lidro.create_virtual_point.stats.calculate_stat import calculate_quartile
from lidro.create_virtual_point.stats.knn_distance import find_k_nearest_neighbors
from lidro.create_virtual_point.vectors.points_along_skeleton import (
    generate_points_along_skeleton,
)


def apply_buffers_to_geometry(hydro_mask, buffer: float):
    """Buffer geometry
    Objective: create a HYDRO mask largest

    Args:
        hydro_mask (gpd.GeoDataFrame): geopandas dataframe with input geometry
        buffer (float): buffer to apply to the input geometry
    Returns:
        GeoJSON: updated geometry
    """
    # Buffer
    geom = hydro_mask.buffer(buffer, cap_style=CAP_STYLE.square)
    return geom


def filter_las_around_point(
    file_skeleton: str,
    file_mask: str,
    file_lidar: str,
    distance_meters: float,
    k: int,
    classes: List[int],
    crs: str | int,
) -> List:
    """Extract a Z elevation value every 2 meters along the hydrographic skeleton

    Args:
        file_skeleton (str): Path from Skeleton
        file_mask (str): Path from Mask Hydro
        file_lidar (str): Path to the input LAS/LAZ file
        distance_meters (float): distance in meters betwen each point
        k (int): The number of nearest neighbors to find
        classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored)
        crs (str | int): Make a CRS from an EPSG code : CRS WKT string

    Returns:
        List : Result {'geometry': Point 3D, 'z_q1': points KNN}
    """
    # Read Mask Hydro merged
    gdf = gpd.read_file(file_mask, crs=crs).unary_union

    # Apply buffer (2 meters) from Mask Hydro
    gdf = apply_buffers_to_geometry(gdf, 2)

    # Create severals points every 2 meters (by default) along skeleton Hydro
    # Return GeoDataframe
    points_gdf = generate_points_along_skeleton(file_skeleton, distance_meters, crs)

    points_list = [([geom.x, geom.y, 0]) for geom in points_gdf.geometry if isinstance(geom, Point)]

    # Filter pointcloud by classes: keep only points from selected classe(s) ("2" : DEFAULT)
    # Crop filtered pointcloud by Mask HYDRO who have a buffer
    points_clip = crop_pointcloud_by_points(file_lidar, str(gdf.wkt), classes)

    # Finds the K nearest neighbors of a given point from a list of 3D points
    points_knn_list = [
        ({"geometry": Point(point), "points_knn": find_k_nearest_neighbors(point, points_clip, k)})
        for point in points_list
    ]

    # Calcule Z "Q1" for each points every 2 meters (by default) along skeleton hydro
    results = [
        ({"geometry": p["geometry"], "z_q1": calculate_quartile(p["points_knn"], 10)})
        for p in points_knn_list
        if not np.all(np.isnan(p["points_knn"]))
    ]

    return results
