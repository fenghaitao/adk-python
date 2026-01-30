"""Pytest configuration and fixtures for LightRAG tests."""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add lightrag to path
LIGHTRAG_PATH = Path(__file__).parent.parent.parent / "lightrag"
sys.path.insert(0, str(LIGHTRAG_PATH))

# Add package to path
PACKAGE_PATH = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(PACKAGE_PATH))


@pytest.fixture
def temp_storage_dir():
    """Provide a temporary storage directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_book_path():
    """Provide path to sample_book.txt fixture."""
    return Path(__file__).parent / "fixtures" / "sample_book.txt"


@pytest.fixture
def sample_book_content(sample_book_path):
    """Provide content of sample_book.txt."""
    with open(sample_book_path, 'r') as f:
        return f.read()


@pytest.fixture
def test_storage_dir():
    """Provide a test storage directory that persists during test session."""
    storage_dir = Path(__file__).parent / "tmp_test_storage"
    storage_dir.mkdir(exist_ok=True)
    return str(storage_dir)


@pytest.fixture(scope="session")
def github_copilot_available():
    """Check if GitHub Copilot is available."""
    # For now, assume it's available if running tests
    # Could add actual check here
    return True


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require API access"
    )
