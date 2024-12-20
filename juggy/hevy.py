from typing import cast

import requests
from loguru import logger

from juggy import util as u

BASE_URL = "https://api.hevyapp.com/"
PAGE_SIZE = 10


def raise_for_status(response: requests.Response) -> None:
    if str(response.status_code)[0] != "2":
        raise RuntimeError(f"Request failed with status code {response.status_code}: {response.text}")


def get_folders(api_key: str) -> list[dict]:
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
        return cast(list[dict], routine_folders)
    else:
        return []


def create_folder(api_key: str, title: str) -> dict:
    """Create a folder in the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    headers = {"api-key": api_key}
    data = {"routine_folder": {"title": title}}

    response = requests.post(url, headers=headers, json=data)
    raise_for_status(response)
    logger.debug(f"Got response: {response}")
    return cast(dict, response.json())


def get_routines(api_key: str) -> list[dict]:
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
    return cast(list[dict], routines)


def create_routine(api_key: str, title: str, folder_id: int, exercises: list[dict]) -> dict:
    """Create a routine in the Hevy API."""
    url = f"{BASE_URL}v1/routines"
    headers = {"api-key": api_key}
    data = {
        "routine": {
            "title": title,
            "folder_id": folder_id,
            "exercises": exercises,
        }
    }

    logger.info(f"Creating routine {title} in folder {folder_id}")
    response = requests.post(url, headers=headers, json=data)
    raise_for_status(response)
    return cast(dict, response.json())


def bootstrap_routines(api_key: str, squats: list[dict], bench: list[dict], deads: list[dict], ohp: list[dict]) -> None:
    """Bootstrap the routines in the Hevy API.

    This will ensure we have 4 routines in a folder named "Juggy":
    - Squat Day
    - Bench Day
    - Deadlift Day
    - OHP Day

    The routines and folder will be created if they don't exist.
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
        folder_id = response["routine_folder"]["id"]
        logger.info(f"Created Juggy folder with id {folder_id}")

    # TODO: lookup and replace each routine
    # routines = get_routines(api_key)

    create_routine(api_key, "Squat Day", folder_id, squats)
    create_routine(api_key, "Bench Day", folder_id, bench)
    create_routine(api_key, "Deadlift Day", folder_id, deads)
    create_routine(api_key, "OHP Day", folder_id, ohp)


def lifts_to_hevy_sets(lifts: list[tuple[float | int, int] | None]) -> list[dict]:
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
    return exercises
