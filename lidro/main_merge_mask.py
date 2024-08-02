""" Main script for calculate Mask HYDRO 1
"""

import logging
import os

import hydra
from omegaconf import DictConfig
from pyproj import CRS

from lidro.merge_mask_hydro.vectors.merge_vector import merge_geom


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    """Merge all vector masks of hydro surfaces from the points classification of the input LAS/LAZ file,
    and save it as a GeoJSON file.

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

    if os.path.isdir(input_dir):
        os.makedirs(output_dir, exist_ok=True)  # Create folder "merge"
        # Merge all Mash Hydro
        merge_geom(
          input_dir, 
          output_dir, 
          CRS.from_user_input(config.io.srid),
          config.mask_generation.vector.min_water_area, 
          config.mask_generation.vector.buffer_positive, 
          config.mask_generation.vector.buffer_negative, 
          config.mask_generation.vector.tolerance)


if __name__ == "__main__":
    main()
