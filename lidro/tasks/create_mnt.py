# -*- coding: utf-8 -*-
""" Create digital model of terrain/surface/height
"""
from typing import List
import pdal



class CreateRaster:
        """Create a digital model of terrain/surface/height from pointclouds
        The interpolator has used "pdal-tin"
        """

        def __init__(
        self,
        nb_pixels: List[int],
        origin: List[float],
        pixel_size: float,
        spatial_ref: str,
        no_data_value: int,
        tile_width: int,
        tile_coord_scale: int,
        classes: List[int],
        ):
            """Initialize the interpolator

            Args:
                nb_pixels (List[int]): number of pixels (nodes) on each axis of the output raster grid
                origin (List[float]): spatial coordinate of the upper-left corner of the raster
                    (center of the upper-left pixel)
                pixel_size (float): distance between each node of the raster grid (in meters)
                spatial_ref (str): spatial reference of the input LAS file
                no_data_value (int): no-data value for the output raster
                tile_width (int): width of the tile in meters (used to infer the lower-left corner for
                    pdal-based interpolators)
                tile_coord_scale (int): scale of the coordinate value contained in the LAS filename
                    (used to infer the coordinates of the raster grid)
                classes (List[int]): List of classes to use for the interpolation (points with other
                    classification values are ignored). If empty, all classes are kept
            """
            self.nb_pixels = nb_pixels
            self.origin = origin
            self.pixel_size = pixel_size
            self.spatial_ref = spatial_ref
            self.no_data_value = no_data_value
            self.tile_width = tile_width
            self.tile_coord_scale = tile_coord_scale
            self.classes = classes

        def execute_pdal_tin(self, fpath: str, output_file: str):
            """Sets up a PDAL pipeline that reads a ground filtered LAS
            file, and interpolates either using "Delaunay", then " Faceraster" and writes it via RASTER. Uses a no-data
            value set in commons.
            More about these in the readme on GitHub.

            The Delaunay Filter creates a triangulated mesh fulfilling the Delaunay condition from a collection of points.

            The FaceRaster filter creates a raster from a point cloud using an algorithm based on an existing
            triangulation.
            Each raster cell is given a value that is an interpolation of the known values of the containing triangle.
            If the raster cell center is outside of the triangulation,
            it is assigned the nodata value. Use writers.raster to write the output.
            The extent of the raster can be defined by using the origin_x, origin_y, width and height options.
            If these options aren’t provided the raster is sized to contain the input data.

            The Raster Writer writes an existing raster to a file. Output is produced using GDAL and can use any driver
            that supports creation of rasters.
            A data_type can be specified for the raster (double, float, int32, etc.).
            If no data type is specified, the data type with the largest range supported by the driver is used.

            Args:
                fpath(str):  input file for the pdal pipeliine
                output_file(str): output file for the pdal pipeliine
            """
            # Read pointcloud
            if not isinstance(self.classes, list):
                raise TypeError("This function's parameter is not good caracter")
            elif not isinstance(self.spatial_ref, str):
                raise TypeError("This function's parameter is not good caracter")
            else:
                pipeline = pdal.Reader.las(filename=fpath, override_srs=self.spatial_ref, nosrs=True)
                if self.classes:
                    pipeline |= pdal.Filter.range(limits=",".join(f"Classification[{c}:{c}]" for c in self.classes))

                pipeline |= pdal.Filter.delaunay()

                pipeline |= pdal.Filter.faceraster(
                        resolution=str(self.pixel_size),
                        origin_x=str(self.origin[0] - self.pixel_size / 2),  # lower left corner
                        origin_y=str(self.origin[1] + self.pixel_size / 2 - self.tile_width),  # lower left corner
                        width=str(self.nb_pixels[0]),
                        height=str(self.nb_pixels[1]),
                )
                pipeline |= pdal.Writer.raster(
                    gdaldriver="GTiff", nodata=self.no_data_value, data_type="float32", filename=output_file
                )
