import geopandas as gpd
from shapely.geometry import Point

from lidro.create_virtual_point.vectors.clip_points_with_bounding_box import (
    clip_points_with_box,
)


def test_create_hydro_vector_mask_default():
    # Define test points (both inside and outside the bounding box)
    points = [
        (830378.719, 6290999.42),  # Inside
        (830382.382, 6290990.115),  # Inside
        (830386.045, 6290980.81),  # Inside
        (830389.709, 6290971.505),  # Inside
        (830216.893, 6291850.548),  # Outside
        (830217.273, 6291840.555),  # Outside
        (830375.000, 6291001.000),  # Outside
        (830400.000, 6291000.000),  # Outside
    ]
    # Convert points to GeoDataFrame
    points_gdf = gpd.GeoDataFrame(geometry=[Point(point) for point in points])

    # Define a bounding box that should clip out some points
    bbox = ((830375, 830390), (6290970, 6291000))

    # Expected points within the bounding box
    expected_points = [
        (830378.719, 6290999.42),
        (830382.382, 6290990.115),
        (830386.045, 6290980.81),
        (830389.709, 6290971.505),
    ]
    # Convert expected points to GeoDataFrame for comparison
    expected_gdf = gpd.GeoDataFrame(geometry=[Point(point) for point in expected_points])

    result_gdf = clip_points_with_box(points_gdf, bbox)

    assert (result_gdf.equals(expected_gdf)) is True
