# -*- coding: utf-8 -*-
""" Create mask non hydro from pointcloud filtering
"""
from typing import Tuple, List
import numpy as np
import scipy.ndimage

from lidro.pointcloud.read_las import read_pointcloud
from lidro.pointcloud.filter_las import filter_pointcloud
from lidro.utils.get_pointcloud_origin import get_pointcloud_origin


class CreateMask:
        """Create aa maks from pointcloud
        """

        def __init__(
        self,
        tile_size: int,
        pixel_size: float,
        spatial_ref: str,
        no_data_value: int,
        ):
            """Initialize the create mask

            Args:
                tile_size (int): tile of the raster grid (in meters)
                pixel_size (float): distance between each node of the raster grid (in meters)
                spatial_ref (str): spatial reference of the input LAS file
                no_data_value (int): no-data value for the output raster
            """
            self.tile_size = tile_size
            self.pixel_size = pixel_size
            self.spatial_ref = spatial_ref
            self.no_data_value = no_data_value

        def binarisation(self, points: np.array, origin: Tuple[int, int]):
            """" Binarisation
            
            Args:
                points (np.array): array from pointcloud
                origin (Tuple[int, int]): spatial coordinate of the upper-left corner of the raster
                    (center of the upper-left pixel)

            Returns:
                bins (np.array): bins
            """
            # Compute number of points per bin
            bins_x = np.arange(origin[0], origin[0] + self.tile_size + self.pixel_size, self.pixel_size)
            bins_y = np.arange(origin[1] - self.tile_size, origin[1] + self.pixel_size, self.pixel_size)
            _bins, _, _ = np.histogram2d(points[:, 1], points[:, 0], bins=[bins_y, bins_x])
            bins = np.flipud(_bins)
            bins = np.where(bins > 0, 0, 1)
            
            return bins
        
        def morphology_math_closing(self, input):
            """ Apply a mathematical morphology operations: closing (dilation + erosion)

            Args:
                input(np.array): bins array
            
            Returns:
                output(np.array): bins array with closing

            """
            output = scipy.ndimage.binary_closing(input, structure=np.ones((5,5))).astype(np.uint8)

            return output

        def create_mask(self, filename: str, classes: List[int]):
            """ Create a mask 

            Args:
                filename(str): input pointcloud
                classes (List[int]): List of classes to use for the binarisation (points with other
                    classification values are ignored).

            Returns:
                bins (np.array): array from pointcloud
            """
            # Read pointcloud, and extract vector of X / Y coordinates of all points 
            array = read_pointcloud(filename) 
            # Extracts parameters for binarisation
            pcd_origin_x, pcd_origin_y = get_pointcloud_origin(array, self.tile_size, 0)

            raster_origin = (pcd_origin_x - self.pixel_size / 2, pcd_origin_y + self.pixel_size / 2)

            # Filter pointcloud by classes [0, 1, 2, 3, 4, 5, 6, 17, 66 ] 
            array_filter = filter_pointcloud(filename, classes) 

            # Binarisation
            _bins = self.binarisation(array_filter, raster_origin)

            # Apply a mathematical morphology operations: clonsing 
            closing_bins = self.morphology_math_closing(_bins)

            return closing_bins

