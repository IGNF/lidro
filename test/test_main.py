import pytest
from pathlib import Path
import subprocess as sp


DATA_PATH = Path("./data/pointcloud/")
TMP_PATH = Path ("./tmp/")


def test_run_main():
    pixel = 1
    cmd = f"""python -m lidro.main \
        -in {str(DATA_PATH)} \
        -o {str(TMP_PATH)} \
        -p {float(pixel)} 
        """
    sp.run(cmd, shell=True, check=True)