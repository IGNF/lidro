# -*- coding: utf-8 -*-
""" Create a raster from pointcloud with severals methods
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

        def create_dtm(self, fpath: str, output_file: str):
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

            pipeline.execute()

        def create_mask_raster(self, fpath: str, output_file: str, method: str):
            """Sets up a PDAL pipeline that reads a filtered LAS
            file, and writes it via GDAL. The GDAL writer has interpolation
            options, exposing the radius, power and a fallback kernel width
            to be configured. More about these in the readme on GitHub.

            The GDAL writer creates rasters using the data specified in the dimension option (defaults to Z).
            The writer creates up to six rasters based on different statistics in the output dataset.
            The order of the layers in the dataset is as follows:
                - min : Give the cell the minimum value of all points within the given radius.
                - max : Give the cell the maximum value of all points within the given radius.
                - mean : Give the cell the mean value of all points within the given radius.
                - idw: Cells are assigned a value based on Shepard’s inverse distance weighting algorithm, considering all
                points within the given radius.

            Args:
                fpath(str):  input file for the pdal pipeliine
                output_file(str): output file for the pdal pipeliine
                method(str): Chose of the method = min / max / mean / idw

                rad(float): Radius about cell center bounding points to use to calculate a cell value.
                [Default: resolution * sqrt(2)]
                pwr(float): Exponent of the distance when computing IDW. Close points have higher significance than far
                points. [Default: 1.0]
                wnd(float): The maximum distance from donor cell to a target cell when applying the fallback interpolation
                method. [default:0]
            """
            pipeline = pdal.Reader.las(filename=fpath, override_srs=self.spatial_ref, nosrs=True)
            if self.classes:
                pipeline |= pdal.Filter.range(limits=",".join(f"Classification[{c}:{c}]" for c in self.classes))
            pipeline |= pdal.Writer.gdal(
                output_type=method,
                resolution=str(self.pixel_size),
                origin_x=str(self.origin[0] - self.pixel_size / 2),  # lower left corner
                origin_y=str(self.origin[1] + self.pixel_size / 2 - self.tile_width),  # lower left corner
                width=str(self.nb_pixels[0]),
                height=str(self.nb_pixels[1]),
                power=2,
                window_size=5,
                nodata=self.no_data_value,
                data_type="float32",
                filename=output_file,
            )

            pipeline.execute()