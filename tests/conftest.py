"""Configuration for the pytest test suite."""

import pytest

from czds import CZDS

# from czds import CZDS
from czds.__main__ import main


@pytest.fixture
def main_class() -> CZDS:
    """Fixture for the main CZDS class interface."""
    return CZDS


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return main()
