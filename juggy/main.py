"""Main application module."""
import juggy.algo as a

BENCH_TM = 220
SQUAT_TM = 285
OHP_TM = 130
DEADLIFT_TM = 430

squats = a.generate_lifts(a.TEMPLATE[0][2], SQUAT_TM, 5, False)
bench = a.generate_lifts(a.TEMPLATE[0][2], BENCH_TM, 5, False)
deads = a.generate_lifts(a.TEMPLATE[0][2], DEADLIFT_TM, 5, True)
ohp = a.generate_lifts(a.TEMPLATE[0][2], OHP_TM, 5, False)
