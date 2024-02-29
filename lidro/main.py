""" Main script for calculate Mask HYDRO 1
"""
import os
import argparse
import logging
from pathlib import Path

from lidro.create_mask_hydro import create_MaskHydro

def parse_args():
    """Arguments
    """
    parser = argparse.ArgumentParser(description="Create Mask Hydro 1 by tile")
    parser.add_argument(
        "-in",
        "--input_dir",
        type=Path,
        required=True,
        help="folder who contains the severals input pointcloud",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=Path,
        required=True,
        help="folder who saves the severals hydro's mask",
    )
    parser.add_argument(
        "-p", "--pixel_size", type=float, default=1, required=True, help="Pixel size"
    )
    parser.add_argument(
        "-t", "--tile_size", type=int, default=1000, required=False, help="tile of the raster grid (in meters)"
    )
    parser.add_argument(
        "-c", "--classe", type=list, default=[0, 1, 2, 3, 4, 5, 6, 17, 66], required=False, help="tList of classes to use for the binarisation (points with other classification values are ignored)"
    )
    parser.add_argument(
        "-e", "--crs", type=str, required=False, help="a pyproj CRS object", default='PROJCS["RGF93 v1 / Lambert-93",GEOGCS["RGF93 v1",DATUM["Reseau_Geodesique_Francais_1993_v1",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],\
         AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
         UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4171"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",3],\
         PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","2154"]]'
    )
    return parser.parse_args()

def run(input_dir: Path, output_dir: Path, pixel_size: float, tile_size: int, classe: list, crs: str):
    """Run function "create_mask_hydro" on single tile useing hydra config
    config parameters are explained in the default.yaml files

    Args:
        - input_dir(Path): path to input (folder)
        - output_dir(Path): path to output (folder)
        - pixel_size (float): distance between each node of the raster grid (in meters)
        - tile_size (int): tile of the raster grid (in meters)
        - classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored).
        - crs (str): a pyproj CRS object
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # List of tile
    if os.path.isdir(input_dir):
        for file in os.listdir(input_dir):
            tilename, _ = os.path.splitext(file)
            input_file = os.path.join(input_dir, f"{tilename}{_}")
            output_file = os.path.join(output_dir, f"MaskHydro_{tilename}.GeoJSON")
            # Lauch the create Hydro's Mask
            create_MaskHydro(input_file, output_file, pixel_size, tile_size, classe, crs)

def main():
    logging.basicConfig(level=logging.INFO)

    args = parse_args()
    run(
        args.input_dir,
        args.output_dir,
        args.pixel_size,
        args.tile_size,
        args.classe,
        args.crs,
    )

if __name__ == "__main__":
    main()
