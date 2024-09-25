import os
import subprocess as sp
from pathlib import Path

from hydra import compose, initialize

from lidro.main_clip_virtual_point_by_tile import main

INPUT_DIR = Path("data/pointcloud")
INPUT_DIR_POINT_VIRTUAL = Path("data/point_virtual")
OUTPUT_DIR = Path("tmp") / "clip_virtual_point_by_tile/main"


def setup_module(module):
    os.makedirs("tmp/clip_virtual_point_by_tile/main", exist_ok=True)


def test_main_run_okay():
    repo_dir = Path.cwd().parent
    cmd = f"""python -m lidro.main_clip_virtual_point_by_tile \
        io.input_dir="{repo_dir}/lidro/data/pointcloud/"\
        io.input_dir_point_virtual="{repo_dir}/lidro/data/point_virtual/"\
        io.output_dir="{repo_dir}/lidro/tmp/clip_virtual_point_by_tile/main/"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_clip_virtual_point_by_tile():
    input_dir = INPUT_DIR
    input_dir_point_virtual = INPUT_DIR_POINT_VIRTUAL
    output_dir = OUTPUT_DIR / "main_clip_virtual_point_by_tile"
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    srid = 2154

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_filename={input_filename}",
                f"io.input_dir={input_dir}",
                f"io.input_dir_point_virtual={input_dir_point_virtual}",
                f"io.output_dir={output_dir}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "tiles_from_las.GeoJSON").is_file()
    assert (Path(output_dir) / input_filename).is_file()
