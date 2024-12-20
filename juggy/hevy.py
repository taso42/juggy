from loguru import logger
import requests

BASE_URL = "https://api.hevyapp.com/"
PAGE_SIZE = 10


def get_folders(api_key: str) -> list[dict]:
    """Get all the folders from the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    params = {"page": 1, "pageSize": PAGE_SIZE}
    headers = {"api-key": api_key}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    results = response.json()
    if "routine_folders" in results:
        page, page_count, routine_folders = (
            results["page"],
            results["page_count"],
            results["routine_folders"],
        )
        # TODO: handle pagination
        logger.info(f"Page {page} of {page_count}")
        return routine_folders
    else:
        return []


def create_folder(api_key: str, title: str) -> dict:
    """Create a folder in the Hevy API."""
    url = f"{BASE_URL}v1/routine_folders"
    headers = {"api-key": api_key}
    data = {"title": title}

    data = {
        "routine_folder": {
            "title": title
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    logger.debug(f"Got response: {response}")
    return response.json()



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
    return routines


def create_routine(api_key: str, title: str, exercises: list[dict]) -> dict:
    """Create a routine in the Hevy API."""
    url = f"{BASE_URL}v1/routines"
    headers = {"api-key": api_key}
    data = {"title": title}

    data = {
        "routine": {
            "title": title,
            "folder_id": None,
            "exercises": [
                {
                    "exercise_template_id": "D04AC939",
                    "sets": [{"type": "normal", "weight_kg": 100, "reps": 10}],
                }
            ],
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def bootstrap_rotines(api_key: str):
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
        logger.info(f"Juggy folder does not exist, creating it")
        response = create_folder(api_key, "Juggy")
        logger.debug(f"Got response: {response}")
        folder_id = response["routine_folder"]["id"]
        logger.info(f"Created Juggy folder with id {folder_id}")
    routines = get_routines(api_key)
    return routines


# {
#   "routine": {
#     "title": "April Leg Day 🔥",
#     "folder_id": null,
#     "notes": "Focus on form over weight. Remember to stretch.",
#     "exercises": [
#       {
#         "exercise_template_id": "D04AC939",
#         "superset_id": null,
#         "rest_seconds": 90,
#         "notes": "Stay slow and controlled.",
#         "sets": [
#           {
#             "type": "normal",
#             "weight_kg": 100,
#             "reps": 10,
#             "distance_meters": null,
#             "duration_seconds": null
#           }
#         ]
#       }
#     ]
#   }
# }

# {
#   "routine": {
#     "title": "April Leg Day 🔥",
#     "exercises": [
#       {
#         "exercise_template_id": "D04AC939",
#         "sets": [
#           {
#             "type": "normal",
#             "weight_kg": 100,
#             "reps": 10
#           }
#         ]
#       }
#     ]
#   }
# }
