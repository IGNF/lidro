import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point

from lidro.create_virtual_point.vectors.flatten_river import flatten_little_river


def test_flatten_little_river_points_knn_not_empty():
    # Create example points GeoDataFrame
    points = gpd.GeoDataFrame(
        {
            "geometry": [Point(0, 0, 10), Point(1, 1, 20), Point(2, 2, 30)],
            "points_knn": [np.array([[0, 0, 10], [1, 1, 20], [2, 2, 30]]) for _ in range(3)],
        }
    )

    # Create example line GeoDataFrame
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (2, 2)])]})

    # Test when points_knn is not empty
    expected_result = 15.0  # Adjusted to the correct 1st quartile value
    result = flatten_little_river(points, line)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


def test_flatten_little_river_points_knn_empty():
    # Test when points_knn is empty
    empty_points = gpd.GeoDataFrame({"geometry": [Point(0, 0)], "points_knn": [np.array([])]})

    # Create example line GeoDataFrame
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (2, 2)])]})

    expected_result = 0
    result = flatten_little_river(empty_points, line)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


def test_flatten_little_river_duplicate_points():
    # Test with duplicate points
    duplicate_points = gpd.GeoDataFrame(
        {
            "geometry": [Point(0, 0, 10), Point(1, 1, 10), Point(2, 2, 10)],
            "points_knn": [np.array([[0, 0, 10], [1, 1, 10], [2, 2, 10]]) for _ in range(3)],
        }
    )

    # Create example line GeoDataFrame
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (2, 2)])]})

    expected_result = 10
    result = flatten_little_river(duplicate_points, line)
    assert result == expected_result, f"Expected {expected_result}, but got {result}"
