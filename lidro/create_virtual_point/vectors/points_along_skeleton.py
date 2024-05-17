# -*- coding: utf-8 -*-
""" Create severals points every 2 meters (by default) along skeleton Hydro
"""
import os

import geopandas as gpd
from shapely.geometry import LineString, Point
from shapely.ops import linemerge


def generate_points_along_skeleton(input_folder: str, file: str, distance_meters: float, crs: str) -> Point:
    """Create severals points every 2 meters (by default) along skeleton Hydro

    Args:
        input_folder (str): folder wich contains Skeleton Hydro by project
        file (str): filename for creating points
        distance_meters (float): distance in meters betwen each point
        crs (str): a pyproj CRS object used to create the output GeoJSON file

    Returns:
        gpd.GeoDataFrame: Points every 2 meters (by default) along skeleton hydro
    """
    # Read the input file
    gdf = gpd.read_file(os.path.join(input_folder, file), crs=crs)
    gdf_lines = gpd.GeoDataFrame(gdf, crs=crs)

    # Segmentize geometry
    lines = linemerge(gdf.geometry.unary_union)

    merged_line = LineString([point for line in lines.geoms for point in line.coords])

    # Create severals points every "distance meters" along skeleton's line
    points = [
        Point(merged_line.interpolate(distance)) for distance in range(0, int(merged_line.length), distance_meters)
    ]
    points.append(Point(merged_line.coords[-1]))  # ADD last point from line

    # Create an empty list to hold points that intersect with LineStrings
    # Iterate through each point and check if it intersects with any LineString in the GeoDataFrame
    intersecting_points = [point for point in points if any(gdf_lines.geometry.intersects(point.buffer(0.1)))]

    return intersecting_points
