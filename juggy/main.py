"""Main application module."""
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

dotenv.load_dotenv()
api_key = os.getenv("HEVY_API_KEY")

squats = a.generate_lifts(a.TEMPLATE[0][2], SQUAT_TM, 5, False)
bench = a.generate_lifts(a.TEMPLATE[0][2], BENCH_TM, 5, False)
deads = a.generate_lifts(a.TEMPLATE[0][2], DEADLIFT_TM, 5, True)
ohp = a.generate_lifts(a.TEMPLATE[0][2], OHP_TM, 5, False)

h.bootstrap_routines(
    api_key,
    [{"exercise_template_id": SQUAT_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(squats)}],
    [{"exercise_template_id": BENCH_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(bench)}],
    [{"exercise_template_id": DEADLIFT_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(deads)}],
    [{"exercise_template_id": OHP_EXERCISE_ID, "sets": h.lifts_to_hevy_sets(ohp)}],
)
