# -*- coding: utf-8 -*-
""" Run function "extract skeleton by bridge"
"""
from typing import List

import pandas as pd
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points


def sort_skeleton_points_by_proximity(skeleton: LineString, reference_geometry: Polygon, is_upstream: bool):
    """
    Sort the points of a LineString skeleton based on their proximity to the edge of the reference geometry.

    Args:
        skeleton (LineString): Skeleton geometry to sort.
        reference_geometry (Polygon): Reference geometry (bridge) to sort the skeleton's points by proximity.
        is_upstream (bool): Boolean indicating if the skeleton is upstream or downstream.
                            If True, the farthest point from the bridge is first (upstream).
                            If False, the closest point to the bridge is first (downstream).

    Returns:
        LineString: A sorted LineString with points ordered based on whether the skeleton is upstream or downstream.
    """
    # Find nearest point on the skeleton to the bridge
    reference_point = nearest_points(reference_geometry, skeleton)[0]
    points_with_distance = [(point, Point(point).distance(reference_point)) for point in skeleton.coords]

    # Sort points by their distance to the reference point
    points_with_distance.sort(key=lambda x: x[1])
    sorted_points = [point for point, distance in points_with_distance]

    # If upstream, reverse the order so that the farthest point is first
    if is_upstream:
        sorted_points = sorted_points[::-1]

    return LineString(sorted_points)


def extract_bridge_skeleton_info(bridge: Polygon, list_skeleton_with_z: List):
    """
    Extract intersection information between bridges and skeletons.
    For each intersection, retrieve the bridge geometry, the geometry of the upstream (amont) skeleton,
    the geometry of the downstream (aval) skeleton, the Z value of the last point of the upstream skeleton,
    and the Z value of the first point of the downstream skeleton.

    Args:
        bridge (Polygon): bridge geometries.
        list_skeleton_with_z (list): List of skeletons with Z values and geometries.

    Returns:
        pd.DataFrame: DataFrame containing bridge geometry, upstream skeleton geometry,
                      downstream skeleton geometry, Z value of the last upstream point,
                      and Z value of the first downstream point.
    """
    intersecting_skeletons = [
        skeleton for skeleton in list_skeleton_with_z if bridge.intersects(skeleton["geometry"]).any()
    ]
    list_skeleton = [i for i in intersecting_skeletons if len(intersecting_skeletons) == 2]
    # Check if exactly two skeletons intersect the bridge
    if round(list_skeleton[0]["z_mean"].item(), 2) > round(list_skeleton[1]["z_mean"].item(), 2):
        skeleton_upstream = list_skeleton[0]
        skeleton_downstream = list_skeleton[1]
    else:
        skeleton_upstream = list_skeleton[1]
        skeleton_downstream = list_skeleton[0]

    # Sort the points for upstream and downstream skeletons based on proximity to the bridge
    geometry_upstream_sorted = sort_skeleton_points_by_proximity(
        skeleton_upstream["geometry"].iloc[0], bridge, is_upstream=True
    )
    geometry_downstream_sorted = sort_skeleton_points_by_proximity(
        skeleton_downstream["geometry"].iloc[0], bridge, is_upstream=False
    )

    # Extract the Z value of the last point of the upstream skeleton
    if isinstance(geometry_upstream_sorted, LineString):
        last_point_upstream = list(geometry_upstream_sorted.coords)[-1]  # Get the coordinates of the last point
        z_upstream = last_point_upstream[2]  # The Z value of the last point
    else:
        raise ValueError("Upstream skeleton geometry is not a LineString.")

    # Extract the Z value of the first point of the downstream skeleton
    if isinstance(geometry_downstream_sorted, LineString):
        first_point_downstream = list(geometry_downstream_sorted.coords)[0]  # Get the coordinates of the first point
        z_downstream = first_point_downstream[2]  # The Z value of the first point
    else:
        raise ValueError("Downstream skeleton geometry is not a LineString.")

    # Extract alert if Z value of the upstream skeleton < Z value of the downstream skeleton
    alert = z_upstream < z_downstream

    # Create a DataFrame to return the results
    data = {
        "bridge_geometry": [bridge],
        "upstream_geometry": [geometry_upstream_sorted],
        "downstream_geometry": [geometry_downstream_sorted],
        "z_upstream": [z_upstream],
        "z_downstream": [z_downstream],
        "alert": [alert],
    }

    return pd.DataFrame(data)
