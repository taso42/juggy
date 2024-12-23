import json
from typing import NotRequired, TypedDict, cast

from juggy.hevy import HevyExercise


class Config(TypedDict):
    """Configuration Settings."""

    api_key: str

    squat_tm: float
    bench_tm: float
    deadlift_tm: float
    ohp_tm: float

    folder: str

    # These are the exercise IDs corresponding to the main lifts
    squat_exercise_id: str
    bench_exercise_id: str
    deadlift_exercise_id: str
    ohp_exercise_id: str

    squat_accessories: NotRequired[list[HevyExercise]]
    bench_accessories: NotRequired[list[HevyExercise]]
    deadlift_accessories: NotRequired[list[HevyExercise]]
    ohp_accessories: NotRequired[list[HevyExercise]]


def save_config(config: Config, filename: str = "config.json") -> None:
    with open(filename, "w") as file:
        json.dump(config, file, indent=4)


def load_config(filename: str = "config.json") -> Config:
    with open(filename) as file:
        return cast(Config, json.load(file))
