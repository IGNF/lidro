import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point
from sklearn.neighbors import NearestNeighbors

from lidro.create_virtual_point.vectors.linear_regression_model import (
    calculate_linear_regression_line,
)


def create_knn_column(points):
    if points.empty:
        return points

    # Extracting the 3D points
    coords = np.array([[p.x, p.y, p.z] for p in points.geometry])

    # Using Nearest Neighbors to find the 3 nearest neighbors
    nbrs = NearestNeighbors(n_neighbors=min(3, len(points)), algorithm="ball_tree").fit(coords)
    distances, indices = nbrs.kneighbors(coords)

    # Creating the 'points_knn' column
    points_knn = [coords[indices[i]] for i in range(len(points))]
    points["points_knn"] = points_knn
    return points


def test_calculate_linear_regression_line_default():
    # Create a sample GeoDataFrame with points designed to produce an R² of 0.25
    np.random.seed(0)
    x_coords = np.linspace(0, 100, num=10)
    y_coords = np.linspace(0, 100, num=10)
    z_coords = x_coords * 0.1 + np.random.normal(0, 5, 10)  # Linear relation with noise

    points = gpd.GeoDataFrame(
        {"geometry": [Point(x, y, z) for x, y, z in zip(x_coords, y_coords, z_coords)]}, crs="EPSG:2154"
    )

    # Add the points_knn column
    points = create_knn_column(points)

    # Create a sample GeoDataFrame with a line representing the river (EPSG:2154)
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (100, 100)])]}, crs="EPSG:2154")

    # Define the CRS
    crs = "EPSG:2154"

    # Call the function to test
    model, r2 = calculate_linear_regression_line(points, line, crs)

    # Check that the r2 is within the range [0, 1]
    assert 0 <= r2 <= 1, "The determination coefficient should be between 0 and 1"

    # Check the type of the model
    assert isinstance(model, np.poly1d), "The regression model should be of type np.poly1d"

    # Check the length of the model's coefficients
    assert len(model.coefficients) == 2, "The regression model should be linear with 2 coefficients"

    # Check the model's coefficients are within expected ranges
    expected_slope_range = (0.01, 0.15)  # Adjusted range
    expected_intercept_range = (-10, 10)
    slope, intercept = model.coefficients
    assert (
        expected_slope_range[0] <= slope <= expected_slope_range[1]
    ), f"Slope {slope} is not within the expected range {expected_slope_range}"
    assert (
        expected_intercept_range[0] <= intercept <= expected_intercept_range[1]
    ), f"Intercept {intercept} is not within the expected range {expected_intercept_range}"
    print("All tests passed successfully!")


def test_calculate_linear_regression_line_empty_inputs():
    # Test with empty GeoDataFrames
    points = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:2154")
    line = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:2154")
    crs = "EPSG:2154"

    model, r2 = calculate_linear_regression_line(points, line, crs)
    assert isinstance(model, np.poly1d), "The regression model should be of type np.poly1d"
    assert r2 == 0.0, "The determination coefficient should be 0 for empty inputs"
    print("Empty input test passed successfully!")


def test_calculate_linear_regression_line_single_point():
    # Test with a single point
    points = gpd.GeoDataFrame({"geometry": [Point(0, 0, 0)]}, crs="EPSG:2154")

    # Add the points_knn column
    points = create_knn_column(points)

    # Create a sample GeoDataFrame with a line representing the river (EPSG:2154)
    line = gpd.GeoDataFrame({"geometry": [LineString([(0, 0), (100, 100)])]}, crs="EPSG:2154")

    # Define the CRS
    crs = "EPSG:2154"

    model, r2 = calculate_linear_regression_line(points, line, crs)
    assert isinstance(model, np.poly1d), "The regression model should be of type np.poly1d"
    assert r2 == 0.0, "The determination coefficient should be 0 for a single point input"
    print("Single point input test passed successfully!")
