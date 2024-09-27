""" Main script for create virtuals points
"""

import logging
import os

import hydra
from omegaconf import DictConfig
from pyproj import CRS

from lidro.create_virtual_point.pointcloud.auto_tiling_from_las import (
    create_geojson_from_laz_files,
)
from lidro.create_virtual_point.vectors.run_add_virtual_points_by_tile import (
    compute_virtual_points_by_tiles,
)


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    """Create a virtual point inside hydro surfaces (3D grid) from the points classification of
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

    # Parameters for clip virtual point by tiles
    crs = CRS.from_user_input(config.io.srid)
    input_dir_point_virtual = config.io.input_dir_point_virtual

    # Clip virtual points file by LIDAR tiles
    # Create the tiling of lidar tiles
    json_tiles = os.path.join(output_dir, "tiles_from_las.GeoJSON")
    laz_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir)]
    create_geojson_from_laz_files(laz_files, json_tiles, crs)
    # Clip virtual points (3D point grid in LAZ format) by LIDAR tiles (tiling file)
    virtul_points_file = os.path.join(input_dir_point_virtual, "virtual_points.laz")
    compute_virtual_points_by_tiles(virtul_points_file, json_tiles, input_dir, output_dir)


if __name__ == "__main__":
    main()
