# import pytest
# import os
# from lidro.vectors.convert_to_vector import ConvertVector
# from lidro.rasters.create_mask_raster import CreateMask
# from pathlib import Path
# import numpy as np
# import rasterio

# las_file= "./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz"

# #las_file = "./data/pointcloud/LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.las"
# output_geojson = "./tmp/Semis_2021_0830_6291_LA93_IGN69.geojson"

# @pytest.fixture
# def create_vector_instance():
#     # Create instance from "ConvertVector" for the tests
#     input_pointcloud = las_file
#     tile_size = 1000
#     pixel_size = 1
#     spatial_ref = 'EPSG:2154'
#     return ConvertVector(
#         input_pointcloud=las_file,
#         tile_size=tile_size,
#         pixel_size=pixel_size,
#         spatial_ref=spatial_ref,
#     )

# @pytest.fixture
# def create_raster_instance():
#     # Create instance from "CreateRatser" for the tests
#     tile_size = 1000
#     pixel_size = 1
#     spatial_ref = 'EPSG:2154'
#     no_data_value = -9999
#     return CreateMask(
#         tile_size=tile_size,
#         pixel_size=pixel_size,
#         spatial_ref=spatial_ref,
#         no_data_value=no_data_value,
#     )

# def setup_module(module):
#     os.makedirs('tmp', exist_ok = True)

# def test_input_exist():
#     assert Path(las_file).exists()

# def test_convert_to_vector(create_raster_instance, create_vector_instance):
#     array = create_raster_instance.create_mask(las_file, classes = [0, 1, 2, 3, 4, 5, 6, 17, 66 ])
    
#     create_vector_instance.raster_to_geojson(array, output_geojson)

#     assert Path(output_geojson).exists()