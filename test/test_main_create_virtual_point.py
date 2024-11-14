import os
import shutil
import subprocess as sp
from pathlib import Path

from hydra import compose, initialize

from lidro.main_create_virtual_point import main

INPUT_DIR = Path("data/tile_0830_6291")
OUTPUT_DIR = Path("tmp") / "main_create_virtual_point"


def setup_module(module):
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_main_run_okay():
    output_dir = OUTPUT_DIR / "run_okay"
    cmd = f"""python -m lidro.main_create_virtual_point \
        io.input_dir={INPUT_DIR}\
        io.input_filename=Semis_2021_0830_6291_LA93_IGN69.laz \
        io.input_mask_hydro="{INPUT_DIR}/mask_hydro_merge/MaskHydro_merge.geojson"\
        io.input_skeleton="{INPUT_DIR}/skeleton/skeleton_hydro.geojson"\
        io.dir_points_skeleton="{INPUT_DIR}/virtual_points/"\
        io.output_dir={output_dir}
        """
    sp.run(cmd, shell=True, check=True)

    assert (Path(output_dir) / "virtual_points.laz").is_file()


def test_main_lidro_input_file():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_input_file"
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    input_mask_hydro = INPUT_DIR / "mask_hydro_merge/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton/skeleton_hydro.geojson"
    dir_points_skeleton = INPUT_DIR / "virtual_points"
    srid = 2154
    points_grid_spacing = 1

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_filename={input_filename}",
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.input_mask_hydro={input_mask_hydro}",
                f"io.input_skeleton={input_skeleton}",
                f"io.dir_points_skeleton={dir_points_skeleton}",
                f"io.srid={srid}",
                f"virtual_point.pointcloud.points_grid_spacing={points_grid_spacing}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "virtual_points.laz").is_file()
