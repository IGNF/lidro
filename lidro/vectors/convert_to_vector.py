# -*- coding: utf-8 -*-
""" Convert a raster (array) to vector
"""
import rasterio
from rasterio.features import shapes
from geojson import FeatureCollection, dump
from shapely.geometry import shape
from rasterio.transform import from_origin
import numpy as np

from lidro.pointcloud.read_las import read_pointcloud
from lidro.utils.get_pointcloud_origin import get_pointcloud_origin

class ConvertVector:
        """Convert numpy.array to vector (GeoJSON)
        """

        def __init__(
        self,
        input_pointcloud : str,
        tile_size: int,
        pixel_size: float,
        spatial_ref: str
        ):
            """Initialize the create mask

            Args:
                input_pointcloud (str): las file
                tile_size (int): tile of the raster grid (in meters)
                pixel_size (float): distance between each node of the raster grid (in meters)
                spatial_ref (str): spatial reference of the input LAS file
            """
            self.input_pointcloud = input_pointcloud
            self.tile_size = tile_size
            self.pixel_size = pixel_size
            self.spatial_ref = spatial_ref

        def extract_origin(self):
            """
            Extract a spatial coordinate of the upper-left corner of the raster

            Returns :
                - raster_origin List[int]: spatial coordinate of the upper-left corner of the raster
            """
            # Read pointcloud, and extract vector of X / Y coordinates of all points 
            array = read_pointcloud(self.input_pointcloud) 
            # Extracts parameters for binarisation
            pcd_origin_x, pcd_origin_y = get_pointcloud_origin(array, self.tile_size, 0)

            raster_origin = (pcd_origin_x - self.pixel_size / 2, pcd_origin_y + self.pixel_size / 2)

            return raster_origin

        def raster_to_geojson(self, binary_image, output_geojson):
            """
            Converts a numpy.array representing a binary raster to GeoJSON (multipolygon), with polygon smoothing.

            Args:
            - binary_image (numpy.array): Numpy array representing the binary raster.
            - output_geojson (str): Path to the output GeoJSON file.
            """
            # Read a binary image
            image = binary_image
            # Extract origin
            origin = self.extract_origin()
            origin_x = origin[0]
            origin_y = origin[1]
            # Transform
            transform = from_origin(origin_x, origin_y, self.pixel_size, self.pixel_size)

            results = ({"properties": {"raster_val": v}, "geometry": s}
                            for i, (s, v) in enumerate(shapes(image.astype(np.int16), mask=None, transform=transform)) if v != 0)
            geoms = list(results)

            # filter water's zone : keep only water's area > 1 000 m²
            _json = []
            for i in enumerate(geoms):
                poly  = i[:][1]['geometry']
                area = shape(poly).area
                if area > 1000 :
                    result = {"geometry": poly}
                    _json.append(result)
            
            # Create JSON
            _geojson = ({"type": "Feature", "geometry": i[1]['geometry'], "properties": {"id": i[0], "cls": "0"}}
                    for i in enumerate(_json, 1))
            information = list(_geojson)
            feature_collection = FeatureCollection(information)

            with open(output_geojson, 'w') as f:
                dump(feature_collection, f)
            
