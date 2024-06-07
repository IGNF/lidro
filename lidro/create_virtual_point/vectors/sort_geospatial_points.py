# -*- coding: utf-8 -*-
""" Sorts a list of 2D points based on their distance from the first point in the list
"""
from typing import List

from shapely.geometry import Point


def sort_geospatial_points(points: List, reference_point: Point) -> List:
    """Sorts a list of 2D points in EPSG:2154 (metric) based on their distance
    from the first point in the list (= upstream and downstream by skeleton's section)

    Parameters:
        points (list of dictionnary): A list of tuples where each tuple represents
                                      a point (x, y) in metric coordinates.
        reference_point (Point): upstream by skeleton's section

    Returns:
        list of tuple: The sorted list of points based on their increasing distance from the first point.
    """

    def euclidean_distance(point1, point2):
        """Calculates the Euclidean distance between two points."""
        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    if not points:
        return []

    # Sort the points by distance to the reference point
    sorted_points = sorted(points, key=lambda point: euclidean_distance(reference_point, point["geometry"]))

    return sorted_points
