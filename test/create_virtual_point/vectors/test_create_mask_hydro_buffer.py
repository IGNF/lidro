import os
import shutil
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
from shapely.geometry import MultiPolygon

from lidro.create_virtual_point.vectors.mask_hydro_with_buffer import (
    import_mask_hydro_with_buffer,
)

TMP_PATH = Path("./tmp/create_virtual_point/vectors/create_mask_hydro_buffer/")

file_mask = "./data/tile_0830_6291/mask_hydro_merge/MaskHydro_merge.geojson"
output = Path("./tmp/create_virtual_point/vectors/create_mask_hydro_buffer/MaskHydro_merge_buffer.geojson")


def setup_module(module):
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_create_mask_hydro_buffer_default():
    # Parameters
    buffer = 2
    crs = CRS.from_epsg(2154)

    result = import_mask_hydro_with_buffer(file_mask, buffer, crs)

    # Save the result to GeoJSON
    d = {"nom": "mask_hydro_merge_buffer", "geometry": [result]}
    gdf = gpd.GeoDataFrame(d, crs=crs)
    gdf.to_file(output, driver="GeoJSON", crs=crs)

    assert Path(output).exists()

    gdf = gpd.read_file(output)

    assert not gdf.empty  # GeoDataFrame shouldn't empty
    assert gdf.crs.to_string() == crs  # CRS is identical

    assert all(isinstance(geom, MultiPolygon) for geom in gdf.geometry)  # All geometry should MultiPolygone
