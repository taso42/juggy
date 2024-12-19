"""Tests for utility functions."""

import pytest

from juggy.util import round_weight


@pytest.mark.parametrize(
    "weight,precision,expected",
    [
        (100.0, 5, 100.0),  # Exact multiple of 5
        (102.3, 5, 105.0),  # Round up to next 5
        (97.8, 5, 100.0),  # Round up to next 5
        (45.1, 5, 50.0),  # Round to nearest 5
        (142.6, 2.5, 145),  # Round with different precision
        (67.8, 1, 68.0),  # Round to nearest 1
    ],
)
def test_round_weight(weight, precision, expected):
    """Test rounding weights to specified precision."""
    assert round_weight(weight, precision) == expected


def test_round_weight_defaults():
    """Test round_weight with default precision."""
    assert round_weight(102.3) == 105.0  # Default precision should be 5


@pytest.mark.parametrize(
    "weight,precision",
    [
        ("not a number", 5),
        (100.0, "not a number"),
        (100.0, 0),
        (100.0, -1),
    ],
)
def test_round_weight_invalid_input(weight, precision):
    """Test round_weight with invalid inputs."""
    with pytest.raises((TypeError, ValueError)):
        round_weight(weight, precision)
