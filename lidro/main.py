""" Main script for calculate Mask HYDRO 1
"""
import argparse
import logging
from pathlib import Path

from lidro.vectors.convert_to_vector import vectorize_bins


def parse_args():
    parser = argparse.ArgumentParser(description="Create Mask Hydro 1 by tile")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="input pointcloud",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="output to vector Hydro 1",
    )
    parser.add_argument(
        "-p", "--pixel", type=float, required=True, help="Pixel size"
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=Path,
        default=Path("./configs/config.yaml"),
        help="((options) yaml file containing the parameters used for each class/metric "
        + "if we want to use other values ​​than the default",
    )
    return parser.parse_args()


def Create_MaskHydro1(input: Path, output: Path, pixel: float, config_file: Path):
    """Run vectorize hydro on single tile useing hydra config
    config parameters are explained in the default.yaml files

    Args:
        - input(str): input pointcloud
        - output(str): path to output
        - pixel (float): distance between each node of the raster grid (in meters)
    """
    # parameters 
    print(config_file)
    #vectorize_bins(input, output, tile_size, pixel_size, classes, crs)

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    Create_MaskHydro1(
        args.input,
        args.output,
        args.pixel,
        args.config_file
    )
    # las_file= "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"
    # output= "./tmp/Hydro_0830_6291.geojson"
    # tile_size = 1000
    # pixel_size = 1
    # classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ]
    # crs = 'PROJCS["RGF93 v1 / Lambert-93",GEOGCS["RGF93 v1",DATUM["Reseau_Geodesique_Francais_1993_v1",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],\
    #     AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
    #     UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4171"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",3],\
    #     PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","2154"]]'
    # vectorize_bins(las_file, output, tile_size, pixel_size, classes, crs)

if __name__ == "__main__":
    main()
