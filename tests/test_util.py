"""Tests for utility functions."""

import pytest

from juggy.util import kgs_to_lbs, lbs_to_kgs, round_weight


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
def test_round_weight(weight: float, precision: float, expected: float) -> None:
    """Test rounding weights to specified precision."""
    assert round_weight(weight, precision) == expected


def test_round_weight_defaults() -> None:
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
def test_round_weight_invalid_input(weight: float, precision: float) -> None:
    """Test round_weight with invalid inputs."""
    with pytest.raises((TypeError, ValueError)):
        round_weight(weight, precision)


@pytest.mark.parametrize(
    "lbs,expected_kgs",
    [
        (45, 20.41),  # 45 lbs test case
        (100, 45.36),
        (200, 90.72),
        (0, 0),  # Edge case
    ],
)
def test_lbs_to_kgs(lbs: float, expected_kgs: float) -> None:
    """Test converting pounds to kilograms."""
    assert round(lbs_to_kgs(lbs), 2) == expected_kgs


@pytest.mark.parametrize(
    "kgs,expected_lbs",
    [
        (100, 220.46),  # 100 kg test case
        (20, 44.09),  # Inverse of 45 lbs
        (45, 99.21),
        (0, 0),  # Edge case
    ],
)
def test_kgs_to_lbs(kgs: float, expected_lbs: float) -> None:
    """Test converting kilograms to pounds."""
    assert round(kgs_to_lbs(kgs), 2) == expected_lbs


def test_conversion_roundtrip() -> None:
    """Test that converting from lbs to kgs and back returns the original value."""
    original_lbs = 45
    assert round(kgs_to_lbs(lbs_to_kgs(original_lbs)), 2) == original_lbs
