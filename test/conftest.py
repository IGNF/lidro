import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--return-file", action="store_true", default=False, help="run tests that return a file to visualize results"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "returnfile: marks tests that return a file to visualize results (select with '--return-file')"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--return-file"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --return-file option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
