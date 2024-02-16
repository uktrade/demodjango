import os

import pytest


@pytest.fixture
def mock_environment():
    keys = []

    def set_environment(name: str, value: str):
        os.environ[name] = value
        keys.append(name)

    yield set_environment

    for key in keys:
        del os.environ[key]
