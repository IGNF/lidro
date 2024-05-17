import os

import geopandas as gpd
from shapely.geometry import LineString, Point
from shapely.ops import linemerge


def generate_points_along_skeleton(input_folder: str, output_folder: str, file: str, distance_meters: float, crs: str):
    """Create severals points every 2 meters (by default) along skeleton Hydro

    Args:
        input_folder (str): folder wich contains Skeleton Hydro by project
        output_folder (str): output folder
        file (str): filename for creating points
        distance_meters (float): distance in meters betwen each point
        crs (str): a pyproj CRS object used to create the output GeoJSON file
    """
    # Read the input file
    gdf = gpd.read_file(os.path.join(input_folder, file), crs=crs)
    gdf_lines = gpd.GeoDataFrame(gdf, crs=crs).explode(index_parts=False)

    # Segmentize geometry
    lines = linemerge(gdf.geometry.unary_union)

    merged_line = LineString([point for line in lines.geoms for point in line.coords])

    # Create severals points every "distance meters" along skeleton's line
    points = [
        Point(merged_line.interpolate(distance)) for distance in range(0, int(merged_line.length), distance_meters)
    ]
    points.append(Point(merged_line.coords[-1]))  # ADD last point from line

    # Create an empty list to hold points that intersect with LineStrings
    # Iterate through each point and check if it intersects with any LineString in the GeoDataFrame
    intersecting_points = [point for point in points if any(gdf_lines.geometry.intersects(point.buffer(0.1)))]

    result = gpd.GeoDataFrame(geometry=intersecting_points, crs=crs).explode(index_parts=False)
    result.to_file(os.path.join(output_folder, "Points.geojson"), driver="GeoJSON", crs=crs)
