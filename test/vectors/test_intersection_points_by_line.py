import geopandas as gpd
from shapely.geometry import LineString, Point

# Import the functions from your module
from lidro.create_virtual_point.vectors.intersect_points_by_line import (
    return_points_by_line,
)


def test_return_points_by_line_default():
    # Create a sample GeoDataFrame with points along a river (EPSG:2154)
    points = gpd.GeoDataFrame(
        {"geometry": [Point(700000, 6600000), Point(700001, 6600001), Point(700002, 6600002), Point(700010, 6600010)]},
        crs="EPSG:2154",
    )

    # Create a sample GeoDataFrame with a line representing the river (EPSG:2154)
    line = gpd.GeoDataFrame({"geometry": [LineString([(700000, 6600000), (700002, 6600002)])]}, crs="EPSG:2154")

    # Call the function to test
    result = return_points_by_line(points, line)

    # Expected points are those within the buffer of the line
    expected_points = gpd.GeoDataFrame(
        {"geometry": [Point(700000, 6600000), Point(700001, 6600001), Point(700002, 6600002)]}, crs="EPSG:2154"
    )

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the result contains the expected points
    assert result.equals(expected_points), f"The result does not match the expected points. Got: {result}"
