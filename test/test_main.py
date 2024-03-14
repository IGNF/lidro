import os
import subprocess as sp
from pathlib import Path

from hydra import compose, initialize

from lidro.main import main

INPUT_DIR = Path("data") / "pointcloud"
OUTPUT_DIR = Path("tmp")


def setup_module(module):
    os.makedirs("tmp/main", exist_ok=True)
    os.makedirs("tmp/main_lidro", exist_ok=True)


def test_main_run_okay():
    repo_dir = Path.cwd().parent.parent
    cmd = f"""python -m lidro.main \
        io.input_dir="{repo_dir}/lidro/data/pointcloud/"\
        io.output_dir="{repo_dir}/lidro/tmp/main/"
        """
    sp.run(cmd, shell=True, check=True)


def test_main_lidro_default():
    input_dir = INPUT_DIR
    output_dir = OUTPUT_DIR / "main_lidro"
    pixel_size = 1
    tile_size = 1000
    srid = 2154
    with initialize(version_base="1.2", config_path="../configs"):
        # config is relative to a module
        cfg = compose(
            config_name="configs_lidro",
            overrides=[
                f"io.input_dir={input_dir}",
                f"io.output_dir={output_dir}",
                f"io.pixel_size={pixel_size}",
                f"io.tile_size={tile_size}",
                f"io.srid={srid}",
            ],
        )
    main(cfg)
    assert (Path(output_dir) / "MaskHydro_LHD_FXX_0706_6627_PTS_C_LAMB93_IGN69_TEST.GeoJSON").is_file()
