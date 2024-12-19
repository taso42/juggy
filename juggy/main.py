"""Main application module."""
import os

import dotenv

SQUAT_TM = 285
BENCH_TM = 220
OHP_TM = 130
DEADLIFT_TM = 430

print("Hello, world!")
for wave in range(4):
    print("wave", wave)

dotenv.load_dotenv()

print(os.getenv("HEVY_API_KEY"))
