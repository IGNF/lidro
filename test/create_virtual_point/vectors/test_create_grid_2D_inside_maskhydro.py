import geopandas as gpd
from shapely.geometry import Polygon

from lidro.create_virtual_point.vectors.create_grid_2D_inside_maskhydro import (
    generate_grid_from_geojson,
)


def test_generate_grid_from_geojson_default():
    # Create a sample GeoDataFrame with a smaller polygon (200m x 200m) in EPSG:2154
    polygon = Polygon([(700000, 6600000), (700000, 6600200), (700200, 6600200), (700200, 6600000), (700000, 6600000)])
    mask_hydro = gpd.GeoDataFrame({"geometry": [polygon]}, crs="EPSG:2154")

    # Define the spacing and margin
    spacing = 0.5  # 0.5 meter spacing
    margin = 0  # no marging

    # Call the function to test
    result = generate_grid_from_geojson(mask_hydro, spacing, margin)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the points are within the polygon bounds
    assert result.within(polygon).all(), "All points should be within the polygon"


def test_generate_grid_from_geojson():
    # Create a sample GeoDataFrame with a smaller polygon (200m x 200m) in EPSG:2154
    polygon = Polygon([(700000, 6600000), (700000, 6600200), (700200, 6600200), (700200, 6600000), (700000, 6600000)])
    mask_hydro = gpd.GeoDataFrame({"geometry": [polygon]}, crs="EPSG:2154")

    # Define the spacing and margin
    spacing = 2  # 2 meter spacing
    margin = 1  # 1 meter marging

    # Call the function to test
    result = generate_grid_from_geojson(mask_hydro, spacing, margin)

    # Check that the result is a GeoDataFrame
    assert isinstance(result, gpd.GeoDataFrame), "The result should be a GeoDataFrame"

    # Check that the points are within the polygon bounds
    assert result.within(polygon).all(), "All points should be within the polygon"
