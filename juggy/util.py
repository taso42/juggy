"""Utility functions for weight calculations."""

import math
from typing import Union


def round_weight(weight: int | float, precision: int | float = 5) -> float:
    """Round a weight to the nearest multiple of the specified precision."""
    if precision <= 0:
        raise ValueError("Precision must be greater than 0")

    return math.ceil(weight / precision) * precision