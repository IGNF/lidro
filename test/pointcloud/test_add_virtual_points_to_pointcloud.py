import os
import shutil
from pathlib import Path

import pdal
from shapely.geometry import Polygon

from lidro.create_virtual_point.pointcloud.add_virtual_points_to_pointcloud import (
    add_virtual_points_by_tiles,
)

# Path to temporary directory for output files
TMP_PATH = Path("./tmp/virtual_points/pointcloud/add_virtual_points_by_tiles")
input_file = str("./data/point_virtual/virtual_points.laz")
input_las = str("./data/pointcloud/Semis_2021_0830_6291_LA93_IGN69.laz")
output_laz_file = str(TMP_PATH / "output_0830_6291_with_virtual_points.laz")
geom = Polygon(
    [
        (830000.0, 6290000.0),
        (831000.0, 6290000.0),
        (831000.0, 6291000.0),
        (830000.0, 6291000.0),
        (830000.0, 6290000.0),
    ]
)


def setup_module():
    """Setup function to ensure the temporary directory is clean before tests."""
    if TMP_PATH.is_dir():
        shutil.rmtree(TMP_PATH)
    os.makedirs(TMP_PATH)


def test_add_virtual_points_by_tiles():
    """Test that the output file is in the correct LAZ format."""
    add_virtual_points_by_tiles(input_file, input_las, output_laz_file, geom)

    # Check that the output file exists
    assert os.path.exists(output_laz_file), "Output LAZ file should be created."

    # Verify the format using PDAL
    pipeline_input = pdal.Pipeline() | pdal.Reader.las(input_file, nosrs=True)
    pipeline_input.execute()

    pipeline_virtual_point = pdal.Pipeline() | pdal.Reader.las(input_las, nosrs=True)
    pipeline_virtual_point.execute()

    pipeline_output = pdal.Pipeline() | pdal.Reader.las(output_laz_file, nosrs=True)
    pipeline_output.execute()

    # Check if the point count for input, virtual points and output
    point_count_input = pipeline_input.metadata["metadata"]["readers.las"]["count"]
    point_count_virtual_point = pipeline_virtual_point.metadata["metadata"]["readers.las"]["count"]
    point_count_output = pipeline_output.metadata["metadata"]["readers.las"]["count"]

    assert point_count_output == int(
        point_count_input + point_count_virtual_point
    ), "The output LAZ file should contain points."
