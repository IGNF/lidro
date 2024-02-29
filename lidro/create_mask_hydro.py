""" Main script for calculate Mask HYDRO 1
"""
import logging

from lidro.vectors.convert_to_vector import vectorize_bins


def create_MaskHydro(input: str, output: str, pixel_size: float, tile_size: int, classe: list, crs: str):
    """Run function "create_mask_hydro" on single tile 

    Args:
        - input(str): input pointcloud
        - output(str): mask hydro (GeoJSON)
        - pixel_size (float): distance between each node of the raster grid (in meters)
        - tile_size (int): tile of the raster grid (in meters)
        - classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored).
        - crs (str): a pyproj CRS object
    """
    logging.basicConfig(level=logging.INFO)
    vectorize_bins(input, output, pixel_size, tile_size, classe, crs)


