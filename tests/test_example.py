"""Example test file."""

import pytest
from wizelit_sdk import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.1"


def test_example():
    """Example test case."""
    assert True

