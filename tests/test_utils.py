"""Tests for utility functions."""

import pytest
from wizelit_sdk.wizelit_agent_wrapper import greet


def test_greet_with_name():
    """Test greet function with a name."""
    result = greet("Alice")
    assert result == "Hello, Alice!"


def test_greet_default():
    """Test greet function with default name."""
    result = greet()
    assert result == "Hello, World!"


def test_greet_empty_string():
    """Test greet function with empty string."""
    result = greet("")
    assert result == "Hello, !"

