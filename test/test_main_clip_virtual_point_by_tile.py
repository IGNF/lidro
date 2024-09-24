import os
import subprocess as sp
from pathlib import Path

from hydra import compose, initialize

from lidro.main_create_virtual_point import main

INPUT_DIR = Path("data/pointcloud")
OUTPUT_DIR = Path("tmp") / "clip_virtual_point_by_tile/main"


def setup_module(module):
    os.makedirs("tmp/create_virtual_point/main", exist_ok=True)


def test_main_run_okay():
    repo_dir = Path.cwd().parent
    cmd = f"""python -m lidro.main_clip_virtual_point_by_tile \
        io.input_dir="{repo_dir}/lidro/data/pointcloud/"\
        io.output_dir="{repo_dir}/lidro/tmp/clip_virtual_point_by_tile/main/"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_lidro_input_file():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro_input_file"
    input_filename = "Semis_2021_0830_6291_LA93_IGN69.laz"
    srid = 2154

    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_filename={input_filename}",
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "tiles_from_las.GeoJSON").is_file()
