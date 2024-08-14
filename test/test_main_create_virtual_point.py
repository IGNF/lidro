import os
import subprocess as sp
from pathlib import Path

from hydra import compose, initialize

from lidro.main_create_virtual_point import main

INPUT_DIR = Path("data")
OUTPUT_DIR = Path("tmp") / "create_virtual_point/main"


def setup_module(module):
    os.makedirs("tmp/create_virtual_point/main", exist_ok=True)


def test_main_run_okay():
    repo_dir = Path.cwd().parent
    cmd = f"""python -m lidro.main_create_virtual_point \
        io.input_dir="{repo_dir}/lidro/data/"\
        io.input_filename=Semis_2021_0830_6291_LA93_IGN69.laz \
        io.input_mask_hydro="{repo_dir}/lidro/data/merge_mask_hydro/MaskHydro_merge.geojson"\
        io.input_skeleton="{repo_dir}/lidro/data/skeleton_hydro/Skeleton_Hydro_small.geojson"\
        io.input_dir_point_skeleton="{repo_dir}/lidro/data/virtual_point/Semis_2021_0830_6291_LA93_IGN69_points_skeleton.geojson"\
        io.output_dir="{repo_dir}/lidro/tmp/create_virtual_point/main/"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_lidro_input_file():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_input_file"
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    input_mask_hydro = INPUT_DIR / "merge_mask_hydro/MaskHydro_merge.geojson"
    input_skeleton = INPUT_DIR / "skeleton_hydro/Skeleton_Hydro_small.geojson"
    input_dir_point_skeleton = INPUT_DIR / "virtual_point/Semis_2021_0830_6291_LA93_IGN69_points_skeleton.geojson"
    srid = 2154
    s = 1
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
                f"io.input_dir_point_skeleton={input_dir_point_skeleton}",
                f"io.srid={srid}",
                f"virtual_point.vector.s={s}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "virtual_points.las").is_file()
