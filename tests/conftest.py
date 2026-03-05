"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tempfile

import pytest


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def clean_environment():
    """Clean and restore environment variables."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings between tests."""
    from config import _settings

    original_settings = _settings
    yield
    # Reset to None to force reload
    globals()['_settings'] = original_settings
