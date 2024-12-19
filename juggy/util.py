"""Utility functions for weight calculations."""

import math

# Number of kilograms in one pound
LBS_TO_KGS_RATIO = 0.45359237


def round_weight(weight: int | float, precision: int | float = 5) -> float:
    """Round a weight to the nearest multiple of the specified precision."""
    if precision <= 0:
        raise ValueError("Precision must be greater than 0")

    return math.ceil(weight / precision) * precision


def lbs_to_kgs(lbs: int | float) -> float:
    """Convert lbs to kg."""
    return lbs * LBS_TO_KGS_RATIO


def kgs_to_lbs(kgs: int | float) -> float:
    """Convert kgs to lbs."""
    return kgs / LBS_TO_KGS_RATIO
