""" Main script for creating N points along Skeleton
"""

import logging
import os

import hydra
from omegaconf import DictConfig
from pyproj import CRS

from lidro.create_virtual_point.vectors.extract_points_around_skeleton import (
    extract_points_around_skeleton_points_one_tile,
)
from lidro.create_virtual_point.vectors.mask_hydro_with_buffer import (
    import_mask_hydro_with_buffer,
)
from lidro.create_virtual_point.vectors.points_along_skeleton import (
    generate_points_along_skeleton,
)


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    """Create N points along Skeleton from the points classification of
    the input LAS/LAZ file and the Hydro Skeleton (GeoJSON). Save a result by LIDAR tiles.

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
    classes = config.virtual_point.filter.keep_neighbors_classes
    k = config.virtual_point.vector.k

    # Step 1 : Import Mask Hydro, then apply a buffer
    # Return GeoDataframe
    input_mask_hydro_buffer = import_mask_hydro_with_buffer(input_mask_hydro, buffer, crs).wkt

    # Step 2 : Create several points every 2 meters (by default) along skeleton Hydro
    # Return GeoDataframe
    points_skeleton_gdf = generate_points_along_skeleton(input_skeleton, distance_meters, crs)

    # Step 3 : Extract points around skeleton by tile
    if initial_las_filename:
        # Lauch croping filtered pointcloud by Mask Hydro with buffer by one tile:
        extract_points_around_skeleton_points_one_tile(
            initial_las_filename, input_dir, output_dir, input_mask_hydro_buffer, points_skeleton_gdf, crs, classes, k
        )
    else:
        # Lauch  croping filtered pointcloud by Mask Hydro with buffer tile by tile
        input_dir_points = os.path.join(input_dir, "pointcloud")
        for file in os.listdir(input_dir_points):
            extract_points_around_skeleton_points_one_tile(
                file, input_dir, output_dir, input_mask_hydro_buffer, points_skeleton_gdf, crs, classes, k
            )


if __name__ == "__main__":
    main()
