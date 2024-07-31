import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, Point
from sklearn.neighbors import NearestNeighbors

from lidro.create_virtual_point.vectors.linear_regression_model import (
    calculate_linear_regression_line,
)


def create_knn_column(points):
    # Extracting the 3D points
    coords = np.array([[p.x, p.y, p.z] for p in points.geometry])

    # Using Nearest Neighbors to find the 3 nearest neighbors
    nbrs = NearestNeighbors(n_neighbors=3, algorithm="ball_tree").fit(coords)
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
