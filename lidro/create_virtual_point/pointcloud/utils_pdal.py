# -*- coding: utf-8 -*-
""" Utils PDAL
"""
import pdal


def read_las_file(input_las: str):
    """Read a las file and put it in an array"""
    pipeline = pdal.Pipeline() | pdal.Reader.las(filename=input_las, nosrs=True)
    pipeline.execute()
    return pipeline.arrays[0]


def get_info_from_las(points):
    """Get info from a las to put it in an array"""
    pipeline = pdal.Filter.stats().pipeline(points)
    pipeline.execute()
    return pipeline.metadata


def get_bounds_from_las(in_las: str):
    """Get bounds=([minx,maxx],[miny,maxy]) from las file

    Args:
        in_las (str): Path to the input LAS/LAZ file

    Returns:
        tuple : Bounds = ([minx,maxx],[miny,maxy]) from las file
    """
    metadata = get_info_from_las(read_las_file(in_las))
    xmin = metadata["metadata"]["filters.stats"]["bbox"]["native"]["bbox"]["minx"]
    xmax = metadata["metadata"]["filters.stats"]["bbox"]["native"]["bbox"]["maxx"]
    ymin = metadata["metadata"]["filters.stats"]["bbox"]["native"]["bbox"]["miny"]
    ymax = metadata["metadata"]["filters.stats"]["bbox"]["native"]["bbox"]["maxy"]
    return ([xmin, xmax], [ymin, ymax])
