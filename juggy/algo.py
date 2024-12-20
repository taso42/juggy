"""Implementation of the Juggernaut method algorithm"""
from juggy.util import round_weight

DELOAD_WEEK = [(0.40, 5), (0.50, 5), (0.60, 5)]

"""
Data structure:
[Wave1, Wave2, Wave3, Wave4]

Each Wave is a list of Weeks:
[Week1, Week2, Week3, Deload]

Each Week is a list of (Ratio, Set) tuples:
[(Ratio, Reps), (Ratio, Reps), ...]
"""
TEMPLATE = [
    ## Wave 1 (10's)
    [
        [(0.60, 10), (0.60, 10), (0.60, 10), (0.60, 10), (0.60, 10)],
        [(0.55, 5), (0.625, 5), (0.675, 10), (0.675, 10), (0.675, 10)],
        [(0.50, 5), (0.60, 3), (0.70, 1), (0.75, 10)],
        DELOAD_WEEK,
    ],
    ## Wave 2 (8's)
    [
        [(0.65, 8), (0.65, 8), (0.65, 8), (0.65, 8), (0.65, 8)],
        [(0.60, 3), (0.675, 3), (0.725, 8), (0.725, 8), (0.725, 8)],
        [(0.50, 5), (0.60, 3), (0.70, 2), (0.75, 1), (0.80, 8)],
        DELOAD_WEEK,
    ],
    ## Wave 3 (5's)
    [
        [(0.70, 5), (0.70, 5), (0.70, 5), (0.70, 5), (0.70, 5), (0.70, 5)],
        [(0.65, 2), (0.725, 2), (0.775, 5), (0.775, 5), (0.775, 5), (0.775, 5)],
        [(0.50, 5), (0.60, 3), (0.70, 2), (0.75, 1), (0.80, 1), (0.85, 5)],
        DELOAD_WEEK,
    ],
    ## Wave 4 (3's)
    [
        [(0.75, 3), (0.75, 3), (0.75, 3), (0.75, 3), (0.75, 3), (0.75, 3), (0.75, 3)],
        [(0.70, 1), (0.775, 1), (0.825, 3), (0.825, 3), (0.825, 3)],
        [(0.50, 5), (0.60, 3), (0.70, 2), (0.75, 1), (0.80, 1), (0.85, 1), (0.90, 3)],
        DELOAD_WEEK,
    ],
]


def generate_base_lifts(
    protocol: list[tuple[float, int]], training_max: int, round: int = 5
) -> list[tuple[float, int]]:
    """Generate a list of lifts based on the protocol and training max."""
    if not isinstance(protocol, list):
        raise TypeError("Protocol must be a list")
    if not isinstance(training_max, (int, float)):
        raise TypeError("Training max must be a number")

    lifts = []
    for ratio, reps in protocol:
        weight = round_weight(training_max * ratio, round)
        lifts.append((weight, reps))
    return lifts


def generate_warmups(
    work_set: float, round=5, is_deadlift: bool = False, warmup_sets: int = 4
) -> list[tuple[float, int]]:
    """Generate a list of warmups based on the work set."""

    first_set = 65 if is_deadlift else 45
    inc = (work_set - first_set) / warmup_sets
    warmups = [(first_set, 10)]
    weight = first_set

    for _, reps in zip(range(warmup_sets - 1), [5, 3, 2, 1, 1, 1, 1, 1]):
        weight = round_weight(weight + inc, round)
        warmups.append((weight, reps))
    return warmups


def generate_lifts(
    protocol: list[tuple[float, int]], training_max: float, round: int = 5, is_deadlift: bool = False
) -> list[tuple[float, int]]:
    """Generate the main lifts of the day.

    This function generates a list of lifts based on the protocol and training max.
    It also generates a list of warmups based on the work set.  Warmups and main lifts are partitioned by None.

    Example:
        >>> generate_lifts(TEMPLATE[0][2], 285, 5, False)
        [(45, 10), (70, 5), (95, 3), (120, 2), None, (145, 5), (175, 3), (200, 1), (215, 10)]
    """
    base_lifts = generate_base_lifts(protocol, training_max, round)
    work_set = base_lifts[0][0]
    warmups = generate_warmups(work_set, round, is_deadlift)
    warmups.append(None)

    return warmups + base_lifts
