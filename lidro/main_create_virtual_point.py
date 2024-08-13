""" Main script for calculate Mask HYDRO 1
"""

import ast
import logging
import os
import sys

import geopandas as gpd
import hydra
import pandas as pd
from omegaconf import DictConfig
from pyproj import CRS

sys.path.append('../lidro')

from lidro.create_virtual_point.pointcloud.convert_geodataframe_to_las import (
    geodataframe_to_las,
)
from lidro.create_virtual_point.vectors.merge_skeleton_by_mask import (
    merge_skeleton_by_mask,
)
from lidro.create_virtual_point.vectors.run_create_virtual_points import (
    lauch_virtual_points_by_section,
)


@hydra.main(config_path="../configs/", config_name="configs_lidro.yaml", version_base="1.2")
def main(config: DictConfig):
    """Create a virtual point inside hydro surfaces (3D grid) from the points classification of
    the input LAS/LAZ file and the Hyro Skeleton (GeoJSON) and save it as LAS file.

    It can run either on a single file, or on each file of a folder

    Args:
        config (DictConfig): hydra configuration (configs/configs_lidro.yaml by default)
        It contains the algorithm parameters and the input/output parameters
    """
    logging.basicConfig(level=logging.INFO)
    # Check input/output files and folders
    input_dir = config.io.input_dir
    if input_dir is None:
        raise ValueError("""config.io.input_dir is empty, please provide an input directory in the configuration""")

    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"""The input directory ({input_dir}) doesn't exist.""")

    output_dir = config.io.output_dir
    if output_dir is None:
        raise ValueError("""config.io.output_dir is empty, please provide an input directory in the configuration""")

    os.makedirs(output_dir, exist_ok=True)

    # Parameters for creating virtual point
    input_mask_hydro = config.io.input_mask_hydro
    input_skeleton = config.io.input_skeleton
    input_dir_points_skeleton = config.io.input_dir_points_skeleton
    crs = CRS.from_user_input(config.io.srid)
    s = config.virtual_point.vector.s

    # Step 1 : Merged all "points_aron_skeleton" by lidar tile
    def process_points_knn(points_knn):
        # Check if points_knn is a string and convert it to a list if necessary
        if isinstance(points_knn, str):
            points_knn = ast.literal_eval(points_knn)  # Convert the string to a list of lists

        # Round each coordinate to 8 decimal places
        return [[round(coord, 8) for coord in point] for point in points_knn]

    points_clip_list = [
        {"geometry": row["geometry"], "points_knn": process_points_knn(row["points_knn"])}
        for filename in os.listdir(input_dir_points_skeleton)
        if filename.endswith(".geojson")
        for _, row in gpd.read_file(os.path.join(input_dir_points_skeleton, filename)).iterrows()
    ]
    # List match Z elevation values every N meters along the hydrographic skeleton
    df = pd.DataFrame(points_clip_list)

    # Step 2: Smooth Z by hydro's section
    if not df.empty and "points_knn" in df.columns and "geometry" in df.columns:
        points_gdf = gpd.GeoDataFrame(df, geometry="geometry")
        points_gdf.set_crs(crs, inplace=True)
        # Combine skeleton lines into a single polyline for each hydro entity
        gdf_merged = merge_skeleton_by_mask(input_skeleton, input_mask_hydro, output_dir, crs)

        gdf_virtual_points = [
            lauch_virtual_points_by_section(
                points_gdf,
                gpd.GeoDataFrame([{"geometry": row["geometry_skeleton"]}], crs=crs),
                gpd.GeoDataFrame([{"geometry": row["geometry_mask"]}], crs=crs),
                crs,
                s,
                output_dir,
            )
            for idx, row in gdf_merged.iterrows()
        ]
        logging.info("Calculate virtuals points by mask hydro and skeleton")
        # Save the virtual points (.LAS)
        geodataframe_to_las(gdf_virtual_points, output_dir, crs)
    else:
        logging.error("No valid data found in points_clip for processing.")


if __name__ == "__main__":
    main()
