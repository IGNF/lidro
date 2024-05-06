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
    """Merge all vector masks of hydro surfacesfrom the points classification of the input LAS/LAZ file,
    and save it as a GeoJSON file.

    It can run either on each file of a folder

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

    # Parameters for merging Mask Hydro
    water_area = config.vector.water_area  # keep only water's area (> 150 m² by default)
    buffer_positive = config.vector.buffer_positive  # positive buffer from Mask Hydro
    buffer_negative = config.vector.buffer_negative  # negative buffer from Mask Hydro
    tolerance = config.vector.tolerance  # Tolerance from Douglas-Peucker
    crs = CRS.from_user_input(config.io.srid)

    if os.path.isdir(input_dir):
        os.makedirs(output_dir, exist_ok=True)  # Create folder "merge"
        # Merge all Mash Hydro
        merge_geom(
          input_dir, 
          output_dir, 
          CRS.from_user_input(config.io.srid),
          config.vector.water_area, 
          config.vector.buffer_positive, 
          config.vector.buffer_negative, 
          config.vector.tolerance)


if __name__ == "__main__":
    main()
