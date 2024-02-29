""" Main script for calculate Mask HYDRO 1
"""
import os
import logging
from pathlib import Path
from pyproj import CRS

import hydra
from omegaconf import DictConfig

from lidro.vectors.convert_to_vector import vectorize_bins


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    logging.basicConfig(level=logging.INFO)

    # Check input/output files and folders
    input_dir = config.io.input_dir
    output_dir = config.io.output_dir

    # Parameters for creating Mask Hydro
    pixel_size = config.io.pixel_size
    tile_size = config.io.tile_size
    crs= CRS.from_user_input(config.io.srid)
    classe = config.filter.keep_classes

    if input_dir is None:
        raise RuntimeError(
            """In input you have to give a las, an input directory .
            For more info run the same command by adding --help"""
        )
    
    # Create output folders
    os.makedirs(output_dir, exist_ok=True)


   # Lauch creating mask hydro by tiles 
    if os.path.isdir(input_dir):
        for file in os.listdir(input_dir):
            tilename, _ = os.path.splitext(file)
            input_file = os.path.join(input_dir, f"{tilename}{_}")
            output_file = os.path.join(output_dir, f"MaskHydro_{tilename}.GeoJSON")
            # Lauch the create Hydro's Mask
            logging.info(f"\nStep 1: Create Mask Hydro 1 for tile : {tilename}")
            vectorize_bins(input_file, output_file, pixel_size, tile_size, classe, crs)
    

if __name__ == "__main__":
    main()