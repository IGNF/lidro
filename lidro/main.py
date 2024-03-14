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
    """Create a vector mask of hydro surfaces from the points classification of the input LAS/LAZ file,
    and save it as a GeoJSON file.

    It can run either on a single file, or on each file of a folder

    Args:
        config (DictConfig): hydra configuration (configs/configs_lidro.yaml by default)
        It contains the algorithm parameters and the input/output parameters
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
            raise FileNotFoundError(f"""The input directory ({input_dir}) doesn't exist.""")

    elif initial_las_filename is not None and input_dir is not None:
        tilename = os.path.splitext(initial_las_filename)[0]
        # Lauch creating mask by one tile:
        input_file = os.path.join(input_dir, initial_las_filename)
        output_file = os.path.join(output_dir, f"MaskHydro_{tilename}.GeoJSON")
        logging.info(f"\nCreate Mask Hydro 1 for tile : {tilename}")
        create_hydro_vector_mask(input_file, output_file, pixel_size, tile_size, classe, crs)
    else:
        raise ValueError("""config.io.input_dir is empty, please provide an input directory in the configuration""")


if __name__ == "__main__":
    main()
