"""Main application module."""
import argparse
import os
from typing import cast

import dotenv
from loguru import logger

import juggy.algo as a
import juggy.config as c
import juggy.hevy as h
from juggy import util as u


def lifts_to_hevy_sets(lifts: list[tuple[float | int, int] | None]) -> list[h.HevySet]:
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
    return cast(list[h.HevySet], exercises)


def setup_routines(
    api_key: str,
    config: c.Config,
    squats: list[h.HevyExercise],
    bench: list[h.HevyExercise],
    deads: list[h.HevyExercise],
    ohp: list[h.HevyExercise],
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
    folders = h.get_folders(api_key)

    for folder in folders:
        if folder["title"] == "Juggy":
            folder_id = folder["id"]
            logger.info(f"Found Juggy folder with id {folder_id}")
            break
    else:
        logger.info("Juggy folder does not exist, creating it")
        response = h.create_folder(api_key, "Juggy")
        logger.debug(f"Got response: {response}")
        folder_id = response["id"]
        logger.info(f"Created Juggy folder with id {folder_id}")

    routines = h.get_routines(api_key)

    squat_accessories_id = config["squat_accessories_id"] if "squat_accessories_id" in config else None
    bench_accessories_id = config["bench_accessories_id"] if "bench_accessories_id" in config else None
    deadlift_accessories_id = config["deadlift_accessories_id"] if "deadlift_accessories_id" in config else None
    ohp_accessories_id = config["ohp_accessories_id"] if "ohp_accessories_id" in config else None

    h.create_or_update_routine(api_key, routines, "Squat Day", folder_id, squats, squat_accessories_id)
    h.create_or_update_routine(api_key, routines, "Bench Day", folder_id, bench, bench_accessories_id)
    h.create_or_update_routine(api_key, routines, "Deadlift Day", folder_id, deads, deadlift_accessories_id)
    h.create_or_update_routine(api_key, routines, "OHP Day", folder_id, ohp, ohp_accessories_id)


def setup_week(api_key: str, config: c.Config, wave: int, week: int) -> None:
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
    squats = a.generate_lifts(protocol, config["squat_tm"], 5, False)
    bench = a.generate_lifts(protocol, config["bench_tm"], 5, False)
    deads = a.generate_lifts(protocol, config["deadlift_tm"], 5, True)
    ohp = a.generate_lifts(protocol, config["ohp_tm"], 5, False)

    notes = f"Wave {wave}, Week {week}"

    setup_routines(
        api_key,
        config,
        [{"exercise_template_id": config["squat_exercise_id"], "sets": lifts_to_hevy_sets(squats), "notes": notes}],
        [{"exercise_template_id": config["bench_exercise_id"], "sets": lifts_to_hevy_sets(bench), "notes": notes}],
        [{"exercise_template_id": config["deadlift_exercise_id"], "sets": lifts_to_hevy_sets(deads), "notes": notes}],
        [{"exercise_template_id": config["ohp_exercise_id"], "sets": lifts_to_hevy_sets(ohp), "notes": notes}],
    )


def main() -> None:
    dotenv.load_dotenv()
    api_key = os.getenv("HEVY_API_KEY")

    if not api_key:
        exit("HEVY_API_KEY is not set")

    config = c.load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--command",
        choices=["program", "maxes"],
        required=True,
        help="The command to execute.  `program`will set up the routines for the week. "
        "`maxes` will recompute training maxes for the next wave. "
        "When using `program`, --wave and --week are required. "
        "When using `maxes`, --foo is required",
    )
    parser.add_argument("--wave", type=int, required=True, help="The wave of the program (1-4)")
    parser.add_argument("--week", type=int, help="The week number of the program (1-4)")

    args = parser.parse_args()
    if args.command == "program":
        if not args.wave or not args.week:
            parser.error("Wave and week are required for program")
        setup_week(api_key, config, args.wave, args.week)
    elif args.command == "maxes":
        print("Recomputing training maxes")
        # Walk backwards in training history and find the top set for each lift in the wave. 
        # This might require some heuristical way of searching.
        # Given the wave we're in, we know the expected reps (10, 8, 5, or 3)
        # With the information above in hand, we can recompute the training maxes for the next wave.
        # Print a summary and ask the user to confirm before saving.


if __name__ == "__main__":
    main()
