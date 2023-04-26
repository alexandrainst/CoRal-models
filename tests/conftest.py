"""General functions and fixtures related to `pytest`."""

import sys
from typing import Generator

import pytest
from datasets import DatasetDict
from hydra import compose, initialize
from omegaconf import DictConfig

from coral_models.data import load_data

# Initialise Hydra
initialize(config_path="../config", version_base=None)


def pytest_configure() -> None:
    """Set a global flag when `pytest` is being run."""
    setattr(sys, "_called_from_test", True)


def pytest_unconfigure() -> None:
    """Unset the global flag when `pytest` is finished."""
    delattr(sys, "_called_from_test")


@pytest.fixture(scope="session")
def cfg() -> Generator[DictConfig, None, None]:
    yield compose(config_name="config")


@pytest.fixture(scope="session")
def dataset(cfg) -> Generator[DatasetDict, None, None]:
    yield load_data(cfg)