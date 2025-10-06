from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def source_path():
    return Path(__file__).parent.resolve()


@pytest.fixture(scope="session")
def data_path(source_path):
    return source_path / "data"
