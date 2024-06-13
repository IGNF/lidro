""" Main script for calculate Mask HYDRO 1
"""

import logging
import os

import geopandas as gpd
import hydra
import numpy as np
from omegaconf import DictConfig
from pyproj import CRS
from shapely.geometry import Point

from lidro.create_virtual_point.pointcloud.crop_las import crop_pointcloud_by_points
from lidro.create_virtual_point.vectors.las_around_point import filter_las_around_point
from lidro.create_virtual_point.vectors.mask_hydro_with_buffer import (
    import_mask_hydro_with_buffer,
)
from lidro.create_virtual_point.vectors.points_along_skeleton import (
    generate_points_along_skeleton,
)


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    """Create a virtual point along hydro surfaces from the points classification of
    the input LAS/LAZ file and the Hyro Skeleton (GeoJSON) and save it as LAS file.

    It can run either on a single file, or on each file of a folder

    Args:
        config (DictConfig): hydra configuration (configs/configs_lidro.yaml by default)
        It contains the algorithm parameters and the input/output parameters
    """
    logging.basicConfig(level=logging.INFO)

    # Check input/output files and folders
    input_dir = config.io.input_dir
    if input_dir is None:
        raise ValueError("""config.io.input_dir is empty, please provide an input directory in the configuration""")

    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"""The input directory ({input_dir}) doesn't exist.""")

    output_dir = config.io.output_dir
    if output_dir is None:
        raise ValueError("""config.io.output_dir is empty, please provide an input directory in the configuration""")

    os.makedirs(output_dir, exist_ok=True)

    # If input filename is not provided, lidro runs on the whole input_dir directory
    initial_las_filename = config.io.input_filename

    input_mask_hydro = config.io.input_mask_hydro
    input_skeleton = config.io.input_skeleton

    # Parameters for creating virtual point
    distance_meters = config.virtual_point.vector.distance_meters
    buffer = config.virtual_point.vector.buffer
    crs = CRS.from_user_input(config.io.srid)
    classes = config.virtual_point.filter.keep_classe_ground
    k = config.virtual_point.vector.k

    # Step 1 : Import Mask Hydro, then apply a buffer
    # Return GeoDataframe
    input_mask_hydro_buffer = import_mask_hydro_with_buffer(input_mask_hydro, buffer, crs).wkt

    # Step 2 : Create several points every 2 meters (by default) along skeleton Hydro
    # Return GeoDataframe
    points_gdf = generate_points_along_skeleton(input_skeleton, distance_meters, crs)

    points_list_skeleton = [([geom.x, geom.y, 0]) for geom in points_gdf.geometry if isinstance(geom, Point)]

    # Step 3 : Crope filtered pointcloud by Mask Hydro with buffer
    def extract_points_around_skeleton_points_one_tile(filename):
        """Lauch main.py on one tile

        Args:
            filename (str): filename to the LAS file

        Returns:
            points_clip (np.array) : Numpy array containing point coordinates (X, Y, Z) after filtering and croping
        """
        input_dir_points = os.path.join(input_dir, "pointcloud")
        tilename = os.path.splitext(filename)[0]  # filename to the LAS file
        input_pointcloud = os.path.join(input_dir_points, filename)  # path to the LAS file
        logging.info(f"\nCroping filtered pointcloud by Mask Hydro with buffer for tile : {tilename}")
        points_clip = crop_pointcloud_by_points(input_pointcloud, str(input_mask_hydro_buffer), classes)
        return points_clip

    if initial_las_filename:
        # Lauch croping filtered pointcloud by Mask Hydro with buffer by one tile:
        points_clip = extract_points_around_skeleton_points_one_tile(initial_las_filename)

    else:
        # Lauch  croping filtered pointcloud by Mask Hydro with buffer tile by tile
        input_dir_points = os.path.join(input_dir, "pointcloud")
        points_clip_list = [
            extract_points_around_skeleton_points_one_tile(file) for file in os.listdir(input_dir_points)
        ]
        points_clip = np.vstack(points_clip_list)  # merge ONE numpy.array

    # Step 4 : Extract a Z elevation value every 2 meters along the hydrographic skeleton
    result = filter_las_around_point(points_list_skeleton, points_clip, k)

    # Convert results to GeoDataFrame
    result_gdf = gpd.GeoDataFrame(result)
    result_gdf.set_crs(crs, inplace=True)
    # path to the Points along Skeleton Hydro file
    output_file = os.path.join(output_dir, "Points_Skeleton.GeoJSON")
    # Save to GeoJSON
    result_gdf.to_file(output_file, driver="GeoJSON")


if __name__ == "__main__":
    main()
