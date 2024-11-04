import geopandas as gpd
import numpy as np
import pytest
from shapely import line_merge
from shapely.geometry import LineString, MultiLineString, Point

from lidro.create_virtual_point.vectors.apply_Z_from_grid import (
    calculate_grid_z,
    calculate_grid_z_with_model,
)


@pytest.mark.parametrize(
    "line, points, expected_curvilinear_abs",
    [
        # Single line, points are on the line
        (
            gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (2, 2)])]}, crs="EPSG:4326"),
            gpd.GeoDataFrame({"geometry": [Point(0, 0), Point(1, 1), Point(2, 2)]}, crs="EPSG:4326"),
            [0, np.sqrt(2), np.sqrt(8)],
        ),
        # Single line, points are not on the line
        (
            gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (0, 2)])]}, crs="EPSG:4326"),
            gpd.GeoDataFrame({"geometry": [Point(0, 0), Point(1, 1), Point(2, 2)]}, crs="EPSG:4326"),
            [0, 1, 2],
        ),
        # Multi line, lines are consecutive, points are on the line
        (
            gpd.GeoDataFrame({"geometry": [MultiLineString([[(0, 0), (0, 2)], [(0, 2), (0, 5)]])]}, crs="EPSG:4326"),
            gpd.GeoDataFrame(
                {"geometry": [Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3), Point(0, 4), Point(0, 5)]},
                crs="EPSG:4326",
            ),
            [0, 1, 2, 3, 4, 5],
        ),
        # Multi line, lines are not ordered, points are on the line
        (
            gpd.GeoDataFrame({"geometry": [MultiLineString([[(0, 0), (0, 2)], [(0, 5), (0, 2)]])]}, crs="EPSG:4326"),
            gpd.GeoDataFrame(
                {"geometry": [Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3), Point(0, 4), Point(0, 5)]},
                crs="EPSG:4326",
            ),
            [0, 1, 2, 3, 4, 5],
        ),
    ],
)
def test_calculate_grid_z_with_model(line, points, expected_curvilinear_abs):

    # Sample model function
    def model(x):
        return np.array(x) * 2  # Simple linear model for testing

    line = line_merge(line)  # this step is usually done in combine_skeletons, this step is meant to check
    # the order of the points after applying a line_merge

    # Call the function to test
    result = calculate_grid_z_with_model(points, line, model)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the result has the same number of points
    assert len(result) == len(points), "The number of points should be the same"

    # Check the Z values
    expected_z = model(expected_curvilinear_abs)
    result_z = result.geometry.apply(lambda geom: geom.z)

    # Use assert_array_almost_equal to check the values
    np.testing.assert_array_almost_equal(
        result_z, expected_z, decimal=5, err_msg="Z values do not match the expected values"
    )


def test_calculate_grid_z_for_flattening():
    # Create a sample GeoDataFrame of points
    points = gpd.GeoDataFrame({"geometry": [Point(0, 0), Point(1, 1), Point(2, 2)]}, crs="EPSG:4326")

    # Predicted Z for flattening
    predicted_z = 10.0

    # Call the function to test
    result = calculate_grid_z(points, predicted_z)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the result has the same number of points
    assert len(result) == len(points), "The number of points should be the same"

    # Check the Z values
    result_z = result.geometry.apply(lambda geom: geom.z)
    assert (result_z == predicted_z).all(), "All Z values should be equal to predicted_z"
