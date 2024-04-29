""" Main script for calculate Mask HYDRO 1
"""

import logging
import os

import hydra
from omegaconf import DictConfig
from pyproj import CRS

from lidro.create_mask_hydro.vectors.convert_to_vector import create_hydro_vector_mask


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

    # Parameters for creating Mask Hydro
    pixel_size = config.io.pixel_size
    tile_size = config.io.tile_size
    crs = CRS.from_user_input(config.io.srid)
    classe = config.filter.keep_classes
    dilation_size = config.raster.dilation_size

    def main_on_one_tile(filename):
        """Lauch main.py on one tile

        Args:
            filename (str): filename to the LAS file
        """
        tilename = os.path.splitext(filename)[0]  # filename to the LAS file
        input_file = os.path.join(input_dir, filename)  # path to the LAS file
        output_file = os.path.join(output_dir, f"MaskHydro_{tilename}.GeoJSON")  # path to the Mask Hydro file
        logging.info(f"\nCreate Mask Hydro 1 for tile : {tilename}")
        create_hydro_vector_mask(input_file, output_file, pixel_size, tile_size, classe, crs, dilation_size)

    if initial_las_filename:
        # Lauch creating mask by one tile:
        main_on_one_tile(initial_las_filename)

    else:
        # Lauch creating Mask Hydro tile by tile
        for file in os.listdir(input_dir):
            main_on_one_tile(file)

if __name__ == "__main__":
    main()
