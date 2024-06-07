# -*- coding: utf-8 -*-
""" Identify upstream and downstream by skeleton's section
"""
from typing import Dict, List, Tuple


def calculate_z_q1_averages(points: List) -> Tuple:
    """Calculate the average 'Z_q1' values for the first 10 percent and the last 10 percent of a list of points

    Parameters:
        points (list): A list of dictionaries where each dictionary contains a 'geometry' key
                       with a Point object and a 'z_q1' key with a numeric value.

    Returns:
        tuple: A pair of values representing the average 'Z_q1' values
               for the first 10 percent and the last 10 percent of the list, respectively.
    """
    total_points = len(points)
    percent_10 = max(1, total_points // 10)  # Ensure at least 1 point to avoid division by zero

    # Extract the first 10 percent and the last 10 percent of points
    first_10_percent_points = points[:percent_10]
    last_10_percent_points = points[-percent_10:]

    # Calculate the average 'Z_q1' values for each group
    average_z_q1_first_10_percent = sum(point["z_q1"] for point in first_10_percent_points) / percent_10
    average_z_q1_last_10_percent = sum(point["z_q1"] for point in last_10_percent_points) / percent_10

    return average_z_q1_first_10_percent, average_z_q1_last_10_percent


def identify_upstream_downstream(points: List) -> Dict:
    """Determinate point for upstream and downstream by skeleton's section

    Args:
        points (List): A list of dictionaries where each dictionary contains a 'geometry' key
                       with a Point object and a 'z_q1' key with a numeric value.

    Returns:
        Dict : A dictionnary representing geometry (Point 2D) and value of "z_q1"
               for upstream and downstream by skeleton's section
    """
    # Calculate the average 'Z_q1' values for the first 10 percent and the last 10 percent of a list of points
    average_z_q1_first_10_percent, average_z_q1_last_10_percent = calculate_z_q1_averages(points)

    if average_z_q1_first_10_percent < average_z_q1_last_10_percent:
        upstream_point = points[0]
        downstream_point = points[-1]
    else:
        upstream_point = points[-1]
        downstream_point = points[0]

    return upstream_point, downstream_point
