import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point

from lidro.create_virtual_point.vectors.apply_Z_from_grid import (
    calculate_grid_z_for_flattening,
    calculate_grid_z_with_model,
)


def test_calculate_grid_z_with_model():
    # Create a sample GeoDataFrame of points
    points = gpd.GeoDataFrame({"geometry": [Point(0, 0), Point(1, 1), Point(2, 2)]}, crs="EPSG:4326")

    # Create a sample GeoDataFrame of line
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (2, 2)])]}, crs="EPSG:4326")

    # Sample model function
    def model(x):
        return np.array(x) * 2  # Simple linear model for testing

    # Call the function to test
    result = calculate_grid_z_with_model(points, line, model)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the result has the same number of points
    assert len(result) == len(points), "The number of points should be the same"

    # Check the Z values
    curvilinear_abs = [0, np.sqrt(2), np.sqrt(8)]
    expected_z = model(curvilinear_abs)
    result_z = result.geometry.apply(lambda geom: geom.z)

    # Use assert_array_almost_equal to check the values
    np.testing.assert_array_almost_equal(
        result_z, expected_z, decimal=5, err_msg="Z values do not match the expected values"
    )


def test_calculate_grid_z_for_flattening():
    # Create a sample GeoDataFrame of points
    points = gpd.GeoDataFrame({"geometry": [Point(0, 0), Point(1, 1), Point(2, 2)]}, crs="EPSG:4326")

    # Create a sample GeoDataFrame of line
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (2, 2)])]}, crs="EPSG:4326")

    # Predicted Z for flattening
    predicted_z = 10.0

    # Call the function to test
    result = calculate_grid_z_for_flattening(points, line, predicted_z)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the result has the same number of points
    assert len(result) == len(points), "The number of points should be the same"

    # Check the Z values
    result_z = result.geometry.apply(lambda geom: geom.z)
    assert (result_z == predicted_z).all(), "All Z values should be equal to predicted_z"
