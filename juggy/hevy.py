from typing import Literal, NotRequired, TypedDict, cast

import requests
from loguru import logger

from juggy import util as u
from juggy.config import Config


class HevySet(TypedDict):
    """A single set in a Hevy exercise."""

    type: Literal["warmup", "normal"]
    weight_kg: float
    reps: int
    # These are returned by the API but should not be set on POSTs and PUTs
    index: NotRequired[int]


class HevyExercise(TypedDict):
    """A single exercise in a Hevy routine."""

    exercise_template_id: str
    notes: str
    sets: list[HevySet]
    # These are returned by the API but should not be set on POSTs and PUTs
    index: NotRequired[int]
    title: NotRequired[str]


class HevyRoutineFolder(TypedDict):
    """A folder containing Hevy routines."""

    id: int
    title: str


class HevyRoutine(TypedDict):
    """A Hevy routine."""

    id: int
    title: str
    notes: str
    folder_id: int
    exercises: list[HevyExercise]


BASE_URL = "https://api.hevyapp.com/"
PAGE_SIZE = 10


def raise_for_status(response: requests.Response) -> None:
    if str(response.status_code)[0] != "2":
        raise RuntimeError(f"Request failed with status code {response.status_code}: {response.text}")


def get_folders(api_key: str) -> list[HevyRoutineFolder]:
    """Get all the folders from the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    params = {"page": 1, "pageSize": PAGE_SIZE}
    headers = {"api-key": api_key}
    response = requests.get(url, params=params, headers=headers)
    raise_for_status(response)
    results = response.json()
    if "routine_folders" in results:
        page, page_count, routine_folders = (
            results["page"],
            results["page_count"],
            results["routine_folders"],
        )
        # TODO: handle pagination
        logger.info(f"Page {page} of {page_count}")
        return cast(list[HevyRoutineFolder], routine_folders)
    else:
        return []


def create_folder(api_key: str, title: str) -> HevyRoutineFolder:
    """Create a folder in the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    headers = {"api-key": api_key}
    data = {"routine_folder": {"title": title}}

    response = requests.post(url, headers=headers, json=data)
    raise_for_status(response)
    logger.debug(f"Got response: {response}")
    return cast(HevyRoutineFolder, response.json())


def get_routines(api_key: str) -> list[HevyRoutine]:
    """Get all the routines from the Hevy API."""
    url = f"{BASE_URL}v1/routines"
    params = {"page": 1, "pageSize": PAGE_SIZE}
    headers = {"api-key": api_key}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    results = response.json()
    page, page_count, routines = (
        results["page"],
        results["page_count"],
        results["routines"],
    )
    # TODO: handle pagination
    logger.info(f"Page {page} of {page_count}")
    return cast(list[HevyRoutine], routines)


def create_or_update_routine(
    api_key: str,
    existing_routines: list[HevyRoutine],
    title: str,
    folder_id: int,
    exercises: list[HevyExercise],
    accessories_id: str,
    notes: str,
) -> HevyRoutine:
    """Create or update a routine in the Hevy API."""
    url = f"{BASE_URL}v1/routines"

    headers = {"api-key": api_key}

    logger.debug(f"Exercises: {exercises}")
    if accessories_id:
        logger.debug(f"Accessories id: {accessories_id}")
        accessories_routine = next((r for r in existing_routines if r["id"] == accessories_id), None)
        logger.debug(f"Accessories routine: {accessories_routine}")
        if accessories_routine:
            accessories_exercises = accessories_routine["exercises"]
            for exercise in accessories_exercises:
                del exercise["index"]
                del exercise["title"]
                for set in exercise["sets"]:
                    del set["index"]
            exercises.extend(accessories_exercises)
            logger.debug(f"Accessories exercises: {accessories_exercises}")

    data = {
        "routine": {
            "title": title,
            "folder_id": folder_id,
            "exercises": exercises,
            # "notes": notes,
        }
    }

    existing_routine = next((r for r in existing_routines if r["title"] == title), None)
    if existing_routine:
        routine_id = existing_routine["id"]
        del data["routine"]["folder_id"]
        logger.info(f"Updating routine {title} with id {routine_id}")
        url = f"{url}/{routine_id}"
        response = requests.put(url, headers=headers, json=data)
        raise_for_status(response)
    else:
        logger.info(f"Creating routine {title} in folder {folder_id}")
        response = requests.post(url, headers=headers, json=data)
        raise_for_status(response)
    return cast(HevyRoutine, response.json())


# TODO: move this into main
def setup_routines(
    api_key: str,
    config: Config,
    notes: str,
    squats: list[HevyExercise],
    bench: list[HevyExercise],
    deads: list[HevyExercise],
    ohp: list[HevyExercise],
) -> None:
    """
    Set up the routines in the Hevy API.

    This will ensure we have 4 routines in a folder named "Juggy":
    - Squat Day
    - Bench Day
    - Deadlift Day
    - OHP Day

    The routines and folder will be created if they don't exist, or updated if they do.
    """
    folders = get_folders(api_key)

    for folder in folders:
        if folder["title"] == "Juggy":
            folder_id = folder["id"]
            logger.info(f"Found Juggy folder with id {folder_id}")
            break
    else:
        logger.info("Juggy folder does not exist, creating it")
        response = create_folder(api_key, "Juggy")
        logger.debug(f"Got response: {response}")
        folder_id = response["id"]
        logger.info(f"Created Juggy folder with id {folder_id}")

    routines = get_routines(api_key)

    squat_accessories_id = config["squat_accessories_id"] if "squat_accessories_id" in config else None
    bench_accessories_id = config["bench_accessories_id"] if "bench_accessories_id" in config else None
    deadlift_accessories_id = config["deadlift_accessories_id"] if "deadlift_accessories_id" in config else None
    ohp_accessories_id = config["ohp_accessories_id"] if "ohp_accessories_id" in config else None

    create_or_update_routine(api_key, routines, "Squat Day", folder_id, squats, squat_accessories_id, notes)
    create_or_update_routine(api_key, routines, "Bench Day", folder_id, bench, bench_accessories_id, notes)
    create_or_update_routine(api_key, routines, "Deadlift Day", folder_id, deads, deadlift_accessories_id, notes)
    create_or_update_routine(api_key, routines, "OHP Day", folder_id, ohp, ohp_accessories_id, notes)


# TODO: move this into main
def lifts_to_hevy_sets(lifts: list[tuple[float | int, int] | None]) -> list[HevySet]:
    """Convert a list of lifts to a list of sets for the Hevy API."""
    exercises = []
    type = "warmup"
    for lift in lifts:
        if lift is None:
            type = "normal"
            continue
        weight_lbs, reps = lift
        weight_kg = u.lbs_to_kgs(weight_lbs)
        exercises.append({"type": type, "weight_kg": weight_kg, "reps": reps})
    return cast(list[HevySet], exercises)
