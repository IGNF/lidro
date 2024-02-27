# -*- coding: utf-8 -*-
""" Vectorize
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from rasterio.transform import from_origin
from rasterio.features import shapes as rasterio_shapes
from shapely.geometry import shape as shapely_shape


from lidro.rasters.create_mask_raster import detect_hydro_by_tile


def vectorize_bins(filename: str, output: str, tile_size: int, pixel_size: float, classes: list, crs: str):
    """ Converts a binary array to GeoJSON (multipolygon), with polygon smoothing.

        Args:
            - filename(str): input pointcloud
            - output(str): path to output
            - tile_size (int): tile of the raster grid (in meters)
            - pixel_size (float): distance between each node of the raster grid (in meters)
            - classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored).
            - crs (dict): a pyproj CRS object
    """
    # Read a binary image representing hydrographic surface(s)
    binary_image, pcd_origin = detect_hydro_by_tile(filename, tile_size, pixel_size, classes)
    
    # Extract origin
    origin_x = pcd_origin[0]
    origin_y = pcd_origin[1]
    # Calculate "transform"
    transform = from_origin(origin_x, origin_y, pixel_size, pixel_size)

    # Convert binary image to vector
    geometry = [shapely_shape(shapedict) for ii, (shapedict, value) in enumerate(rasterio_shapes(
                    binary_image.astype(np.int16), mask=None, connectivity=8, transform=transform)) 
                if value != 0]
    # keep only water's area > 1000 m²
    filter_geometry = [geom for geom in geometry if geom.area > 1000]
    nb_filter_geometry = len(filter_geometry)

    gdf = gpd.GeoDataFrame(
            {"layer": [ii for ii, geom in enumerate(filter_geometry)] * np.ones(nb_filter_geometry), "dalles": filename, "geometry": filter_geometry},
            geometry="geometry",
            crs=crs, 
            )
   
    # save the result
    gdf.to_file(output, driver='GeoJSON', crs=crs)

    


    
