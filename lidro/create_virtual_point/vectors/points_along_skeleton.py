import os

import geopandas as gpd
import shapely
from shapely.geometry import MultiPoint


def generate_points_along_skeleton(input_folder: str, output_folder: str, file: str, distance_meters: float, crs: str):
    """Create severals points every 2 meters (by default) along skeleton Hydro

    Args:
        input_folder (str): folder wich contains Skeleton Hydro by project
        output_folder (str): output folder
        file (str): filename for creating points
        distance_meters (float): distance in meters betwen each point
        crs (str): a pyproj CRS object used to create the output GeoJSON file
    """ """"""
    gdf = gpd.read_file(os.path.join(input_folder, file), crs=crs)

    # Segmentize geometry
    multi_line = shapely.segmentize((gdf["geometry"].unary_union), max_segment_length=distance_meters)

    # Extract Points along skeleton
    points = [point for line in multi_line.geoms for point in line.coords]
    multi_point = MultiPoint(points)

    gdf_final = gpd.GeoSeries(multi_point, crs=crs).explode(index_parts=False)

    gdf_final.to_file(os.path.join(output_folder, "Points.geojson"), driver="GeoJSON", crs=crs)
