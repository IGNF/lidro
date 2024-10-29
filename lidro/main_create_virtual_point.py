""" Main script for create virtuals points
"""

import ast
import logging
import os

import geopandas as gpd
import hydra
import pandas as pd
from omegaconf import DictConfig
from pyproj import CRS

from lidro.create_virtual_point.pointcloud.convert_list_points_to_las import (
    list_points_to_las,
)
from lidro.create_virtual_point.vectors.merge_skeleton_by_mask import (
    merge_skeleton_by_mask,
)
from lidro.create_virtual_point.vectors.rectify_alert import (
    create_list_rectify_skeleton_with_mask,
)
from lidro.create_virtual_point.vectors.run_create_virtual_points import (
    compute_virtual_points_by_section,
)
from lidro.create_virtual_point.vectors.run_update_skeleton_with_z import (
    compute_skeleton_with_z,
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
    input_dir_points_skeleton = config.io.dir_points_skeleton
    input_bridge = config.io.input_bridge
    crs = CRS.from_user_input(config.io.srid)
    river_length = config.virtual_point.vector.river_length
    points_grid_spacing = config.virtual_point.pointcloud.points_grid_spacing
    classes = config.virtual_point.pointcloud.virtual_points_classes

    # Step 1 : Merged all "points around skeleton" by lidar tile
    def process_points_knn(points_knn):
        # Check if points_knn is a string and convert it to a list if necessary
        if isinstance(points_knn, str):
            points_knn = ast.literal_eval(points_knn)  # Convert the string to a list of lists
        return [[round(coord, 3) for coord in point] for point in points_knn]

    points_clip_list = [
        {"geometry": row["geometry"], "points_knn": process_points_knn(row["points_knn"])}
        for filename in os.listdir(input_dir_points_skeleton)
        if filename.endswith(".geojson")
        for _, row in gpd.read_file(os.path.join(input_dir_points_skeleton, filename)).iterrows()
    ]
    # List match Z elevation values every N meters along the hydrographic skeleton
    df = pd.DataFrame(points_clip_list)

    # Step 2: Combine skeleton lines into a single polyline for each hydro entity
    if not df.empty and "points_knn" in df.columns and "geometry" in df.columns:
        points_gdf = gpd.GeoDataFrame(df, geometry="geometry")
        points_gdf.set_crs(crs, inplace=True)
        # Combine skeleton lines into a single polyline for each hydro entity
        gdf_merged = merge_skeleton_by_mask(input_skeleton, input_mask_hydro, output_dir, crs)

        # Step 3 : Apply Z from skeleton
        list_skeleton_with_z = [
            compute_skeleton_with_z(
                points_gdf,
                gpd.GeoDataFrame([{"geometry": row["geometry_skeleton"]}], crs=crs),
                gpd.GeoDataFrame([{"geometry": row["geometry_mask"]}], crs=crs),
                crs,
                river_length,
                output_dir,
            )
            for idx, row in gdf_merged.iterrows()
        ]
        logging.info("Apply Z to skeleton")
        # print(list_skeleton_with_z)

        # Step 4 : intersect skeletons by bridge and return info
        gdf_skeleton_rectify_with_mask = create_list_rectify_skeleton_with_mask(
            input_bridge, input_mask_hydro, list_skeleton_with_z, crs
        )
        logging.info("intersect skeletons by bridge and return info")
        print(gdf_skeleton_rectify_with_mask)

        # Step 5 : Generate a regular grid of 3D points spaced every N meters inside each hydro entity
        list_virtual_points = [
            compute_virtual_points_by_section(
                gpd.GeoDataFrame(geometry=row["geometry"], crs=crs),
                gpd.GeoDataFrame(geometry=row["geometry_mask"], crs=crs),
                crs,
                points_grid_spacing,
            )
            for idx, row in enumerate(gdf_skeleton_rectify_with_mask)
        ]
        logging.info("Calculate virtuals points by mask hydro and skeleton")
        # print(list_virtual_points)

        # Step 6 : Save the virtual points in a file (.LAZ)
        list_points_to_las(list_virtual_points, output_dir, crs, classes)
    else:
        logging.error("Error when merged all points around skeleton by lidar tile")


if __name__ == "__main__":
    main()
