"""Shared pytest fixtures for the KaveriAssets tests."""
import shutil
from datetime import date
from pathlib import Path

import pytest

from kaveriassets.service import AssetService

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def data_dir(tmp_path):
    """A temporary copy of tests/fixtures/ (the original data), so a test can change it safely."""
    target = tmp_path / "data"
    shutil.copytree(FIXTURES, target)
    return target


@pytest.fixture
def service(data_dir):
    """An AssetService on the temporary data."""
    return AssetService(data_dir)


@pytest.fixture
def today():
    """The date the tests treat as 'today'."""
    return date(2026, 12, 1)
