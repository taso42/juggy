"""Implementation of the Juggernaut method algorithm"""


"""
Data structure:
[Wave1, Wave2, Wave3, Wave4]

Each Wave is a list of Weeks:
[Week1, Week2, Week3, Deload]

Each Week is a list of (Ratio, Set) tuples:
[(Ratio, Reps), (Ratio, Reps), ...]
"""

DELOAD_WEEK = [(0.40, 5), (0.50, 5), (0.60, 5)]

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


def generate_lifts(protocol: list[tuple[float, int]], training_max: int) -> list[tuple[float, int]]:
    """Generate a list of lifts based on the protocol and training max."""
    lifts = []
    for ratio, reps in protocol:
        weight = training_max * ratio
        lifts.append((weight, reps))
    return lifts