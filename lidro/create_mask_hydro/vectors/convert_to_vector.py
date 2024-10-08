# -*- coding: utf-8 -*-
""" Vectorize
"""
import geopandas as gpd
import numpy as np
from rasterio.features import shapes as rasterio_shapes
from rasterio.transform import from_origin
from shapely.geometry import shape as shapely_shape

from lidro.create_mask_hydro.rasters.create_mask_raster import detect_hydro_by_tile


def create_hydro_vector_mask(
    filename: str, output: str, pixel_size: float, tile_size: int, classes: list, crs: str, dilatation_size: int
):
    """Create a vector mask of hydro surfaces in a tile from the points classification of the input LAS/LAZ file,
    and save it as a GeoJSON file.


    Args:
        filename (str): path to the input pointcloud
        output (str): path to output geoJSON
        pixel_size (float): distance between each node of the intermediate raster grid (in meters)
        tile_size (int): size of the intermediate raster grid (in meters)
        classes (list): List of classes to consider as water (points with other classification values are ignored)
        crs (str): a pyproj CRS object used to create the output GeoJSON file
        dilatation_size (int): size for dilatation raster
    """
    # Read a binary image representing hydrographic surface(s)
    binary_image, pcd_origin = detect_hydro_by_tile(filename, tile_size, pixel_size, classes, dilatation_size)

    # Extract origin
    origin_x = pcd_origin[0]
    origin_y = pcd_origin[1]
    # Calculate "transform"
    transform = from_origin(origin_x, origin_y, pixel_size, pixel_size)

    # Convert binary image to vector
    geometry = [
        shapely_shape(shapedict)
        for shapedict, value in rasterio_shapes(
            binary_image.astype(np.int16), mask=None, connectivity=8, transform=transform
        )
        if value != 0
    ]
    # save the result
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=crs)
    gdf.to_file(output, driver="GeoJSON", crs=crs)
