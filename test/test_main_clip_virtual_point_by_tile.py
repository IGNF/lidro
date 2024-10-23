import os
import subprocess as sp
from pathlib import Path

from hydra import compose, initialize

from lidro.main_clip_virtual_point_by_tile import main

DATA_DIR = Path("data/tile_0830_6291")
INPUT_DIR = DATA_DIR / "pointcloud"
INPUT_DIR_POINT_VIRTUAL = DATA_DIR / "virtual_points"
OUTPUT_DIR = Path("tmp") / "main_clip_virtual_point_by_tile"


def setup_module(module):
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_main_run_okay():
    output_dir = OUTPUT_DIR / "main_run_okay"
    cmd = f"""python -m lidro.main_clip_virtual_point_by_tile \
        io.input_dir={INPUT_DIR}\
        io.input_dir_point_virtual={INPUT_DIR_POINT_VIRTUAL}\
        io.output_dir={output_dir}
        """
    sp.run(cmd, shell=True, check=True)


def test_main_creates_expected_output():
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    srid = 2154
    output_dir = OUTPUT_DIR / "main_creates_expected_output"

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_filename={input_filename}",
                f"io.input_dir={INPUT_DIR}",
                f"io.input_dir_point_virtual={INPUT_DIR_POINT_VIRTUAL}",
                f"io.output_dir={output_dir}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "tiles_from_las.GeoJSON").is_file()
    assert (Path(output_dir) / input_filename).is_file()
