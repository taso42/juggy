"""Main application module."""
import argparse
import os

import dotenv

import juggy.algo as a
import juggy.hevy as h
from juggy.constants import (
    BENCH_EXERCISE_ID,
    DEADLIFT_EXERCISE_ID,
    OHP_EXERCISE_ID,
    SQUAT_EXERCISE_ID,
)

BENCH_TM = 220
SQUAT_TM = 285
OHP_TM = 130
DEADLIFT_TM = 430


def setup_week(api_key: str, wave: int, week: int) -> None:
    """Setup a week in the Hevy API.

    Args:
        api_key: The API key for the Hevy account.
        wave: The wave of the program (1-4)
        week: The week number of the program (1-4). Every 4th week is a deload week
    """
    if wave < 0 or wave > 4:
        raise ValueError(f"Invalid wave number: {wave}")
    if week < 0 or week > 4:
        raise ValueError(f"Invalid week number: {week}")

    protocol = a.TEMPLATE[wave - 1][week - 1]
    squats = a.generate_lifts(protocol, SQUAT_TM, 5, False)
    bench = a.generate_lifts(protocol, BENCH_TM, 5, False)
    deads = a.generate_lifts(protocol, DEADLIFT_TM, 5, True)
    ohp = a.generate_lifts(protocol, OHP_TM, 5, False)

    h.setup_routines(
        api_key,
        [{"exercise_template_id": SQUAT_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(squats)}],
        [{"exercise_template_id": BENCH_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(bench)}],
        [{"exercise_template_id": DEADLIFT_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(deads)}],
        [{"exercise_template_id": OHP_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(ohp)}],
    )


def main() -> None:
    dotenv.load_dotenv()
    api_key = os.getenv("HEVY_API_KEY", "undefined")

    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", type=int, required=True, help="The wave of the program (1-4)")
    parser.add_argument("--week", type=int, required=True, help="The week number of the program (1-4)")
    args = parser.parse_args()
    setup_week(api_key, args.wave, args.week)


if __name__ == "__main__":
    main()
