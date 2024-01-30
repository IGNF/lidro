# -*- coding: utf-8 -*-
""" Create an inverse raster
"""
import rasterio as rio
import numpy as np


def create_inverse_mask(fpath: str, output_file: str):
    """Create a inverse mask from raster

        Args:
            fpath(str):  input (mask)
            output_file(str): output (inverse mask)
    """
    # Read the data set as numpy array
    ds=rio.open(fpath)
    arr=ds.read(1)
    # The nodata value in the raster dataset is -9999
    arr.min() # Getting the min value in the array
    # Mask the raster using numpy where (if the pixel has value bigger than the minimum value(-9999),
    # its value will change to 1, otherwise its value will change to 0)
    arr=np.where(arr>arr.min(),0,1)
    print(arr)
    # create a new dataset to save the masked array in it
    # crs and transform are optional to be defined, others are necessary
    # Here we create the new data set but
    output = fpath.replace('.tif', '_inverse.tif') # name of output image
    new_ds=rio.open(output,"w",
               driver="GTiff",
               height=ds.height,
               width=ds.width,
               count=1,
               dtype=arr.dtype,
               crs=ds.crs,
               transform=ds.transform)
    new_ds.write(arr, 1)
    new_ds.close()