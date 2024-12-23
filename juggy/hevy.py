from typing import Literal, NotRequired, TypedDict, cast

import requests
from loguru import logger

BASE_URL = "https://api.hevyapp.com/"
PAGE_SIZE = 10


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


class HevyWorkout(TypedDict):
    """A Hevy workout."""

    id: NotRequired[str]
    title: str
    is_private: bool
    start_time: str
    end_time: str
    exercises: list[HevyExercise]


def _raise_for_status(response: requests.Response) -> None:
    if str(response.status_code)[0] != "2":
        raise RuntimeError(f"Request failed with status code {response.status_code}: {response.text}")


def _get_with_paging(api_key: str, url: str, object_name: str, short_circuit: int | None = None) -> list[dict]:
    """Consume an API response with paging."""
    headers = {"api-key": api_key}
    page = 1
    page_count = 1
    all_objects: list[dict] = []
    while page <= page_count:
        params = {"page": page, "pageSize": PAGE_SIZE}
        response = requests.get(url, params=params, headers=headers)
        _raise_for_status(response)
        results = response.json()
        if object_name not in results:
            return []
        page, page_count, objects = (
            results["page"],
            results["page_count"],
            results[object_name],
        )
        logger.debug(f"Page {page} of {page_count}")
        page += 1
        all_objects.extend(objects)
        if short_circuit and len(all_objects) >= short_circuit:
            break

    return all_objects


def get_folders(api_key: str) -> list[HevyRoutineFolder]:
    """Get all the folders from the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    return cast(list[HevyRoutineFolder], _get_with_paging(api_key, url, "routine_folders"))


def get_workouts(api_key: str) -> list[HevyWorkout]:
    """Get all the workouts from the Hevy API.
    Currently returns only the last ~100."""
    url = f"{BASE_URL}v1/workouts"
    return cast(list[HevyWorkout], _get_with_paging(api_key, url, "workouts", 100))


def get_routines(api_key: str) -> list[HevyRoutine]:
    """Get all the routines from the Hevy API."""
    url = f"{BASE_URL}v1/routines"
    return cast(list[HevyRoutine], _get_with_paging(api_key, url, "routines"))


def create_folder(api_key: str, title: str) -> HevyRoutineFolder:
    """Create a folder in the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    headers = {"api-key": api_key}
    data = {"routine_folder": {"title": title}}

    response = requests.post(url, headers=headers, json=data)
    _raise_for_status(response)
    logger.debug(f"Got response: {response}")
    return cast(HevyRoutineFolder, response.json()["routine_folder"])


def create_or_update_routine(
    api_key: str,
    existing_routines: list[HevyRoutine],
    title: str,
    folder_id: int,
    exercises: list[HevyExercise],
    accessories_id: str | None,
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
        }
    }

    existing_routine = next(
        (r for r in existing_routines if (r["title"] == title and r["folder_id"] == folder_id)), None
    )
    if existing_routine:
        routine_id = existing_routine["id"]
        del data["routine"]["folder_id"]
        logger.info(f"Updating routine {title} with id {routine_id}")
        url = f"{url}/{routine_id}"
        response = requests.put(url, headers=headers, json=data)
        _raise_for_status(response)
    else:
        logger.info(f"Creating routine {title} in folder {folder_id}")
        response = requests.post(url, headers=headers, json=data)
        _raise_for_status(response)
    return cast(HevyRoutine, response.json())
