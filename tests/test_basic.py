"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Sample test data."""
    return {"message": "Hello, Vibe Agents!"}


def test_import():
    """Test basic import functionality."""
    import vibe_agents
    assert vibe_agents.__version__ is not None