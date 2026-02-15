"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def tmp_config_dir():
    """Create a temporary config directory."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def tmp_data_dir():
    """Create a temporary data directory."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing."""
    return """content,platforms,scheduled_time,hashtags
"Hello World!",twitter,,"test"
"LinkedIn post",linkedin,,"professional"
"Photo post",instagram,,"visual"
"All platforms post",all,,"everywhere"
"""
