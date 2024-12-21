import json
from typing import TypedDict, cast


class Config(TypedDict):
    """Configuratino Settings."""

    squat_tm: int
    bench_tm: int
    deadlift_tm: int
    ohp_tm: int
    squat_exercise_id: str
    bench_exercise_id: str
    deadlift_exercise_id: str
    ohp_exercise_id: str


def save_config(config: Config, filename: str = "config.json") -> None:
    with open(filename, "w") as file:
        json.dump(config, file, indent=4)


def load_config(filename: str = "config.json") -> Config:
    with open(filename) as file:
        return cast(Config, json.load(file))
