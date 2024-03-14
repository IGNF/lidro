""" Main script for calculate Mask HYDRO 1
"""

import logging
import os

import hydra
from omegaconf import DictConfig
from pyproj import CRS

from lidro.vectors.convert_to_vector import create_hydro_vector_mask


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    """Run HYDRO

    Args:
        config (DictConfig): configs_lidro.yaml with severals parameters

    Raises:
        RuntimeError: Check have a las and an input directory
    """
    logging.basicConfig(level=logging.INFO)

    # Check input/output files and folders
    input_dir = config.io.input_dir
    output_dir = config.io.output_dir

    # Check pointcloud tile
    initial_las_filename = config.io.input_filename

    # Parameters for creating Mask Hydro
    pixel_size = config.io.pixel_size
    tile_size = config.io.tile_size
    crs = CRS.from_user_input(config.io.srid)
    classe = config.filter.keep_classes

    os.makedirs(output_dir, exist_ok=True)

    if initial_las_filename is None and input_dir is not None:
        # Lauch creating mask hydro by tiles
        if os.path.isdir(input_dir):
            for file in os.listdir(input_dir):
                tilename, _ = os.path.splitext(file)
                input_file = os.path.join(input_dir, f"{tilename}{_}")
                output_file = os.path.join(output_dir, f"MaskHydro_{tilename}.GeoJSON")
                logging.info(f"\nCreate Mask Hydro 1 for tile : {tilename}")
                create_hydro_vector_mask(input_file, output_file, pixel_size, tile_size, classe, crs)
        else:
            raise RuntimeError(
                """An input directory doesn't exist.
                For more info run the same command by adding --help"""
            )
    elif initial_las_filename is not None and input_dir is not None:
        tilename = os.path.splitext(initial_las_filename)[0]
        # Lauch creating mask by one tile:
        input_file = os.path.join(input_dir, initial_las_filename)
        output_file = os.path.join(output_dir, f"MaskHydro_{tilename}.GeoJSON")
        logging.info(f"\nCreate Mask Hydro 1 for tile : {tilename}")
        create_hydro_vector_mask(input_file, output_file, pixel_size, tile_size, classe, crs)
    else:
        raise RuntimeError(
            """In input you haven't to give a las, an input directory.
            For more info run the same command by adding --help"""
        )


if __name__ == "__main__":
    main()
