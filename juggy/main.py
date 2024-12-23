"""Main application logic and entry point."""
import argparse
import shutil
from typing import cast

from loguru import logger

import juggy.algo as a
import juggy.config as c
import juggy.hevy as h
from juggy import util as u

ROUND_WEIGHT_PRECISION = 5
ONE_REP_MAX_THRESHOLD = 0.95
BENCH_INCREMENT = 2.5
OHP_INCREMENT = 2.5
SQUAT_INCREMENT = 5
DEADLIFT_INCREMENT = 5


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

    folder_name = config["folder"]
    for folder in folders:
        if folder["title"] == folder_name:
            folder_id = folder["id"]
            logger.info(f"Found {folder_name} folder with id {folder_id}")
            break
    else:
        logger.info(f"{folder_name} folder does not exist, creating it")
        response = h.create_folder(api_key, folder_name)
        logger.debug(f"Got response: {response}")
        folder_id = response["id"]
        logger.info(f"Created {folder_name} folder with id {folder_id}")

    routines = h.get_routines(api_key)

    squat_accessories = config["squat_accessories"] if "squat_accessories" in config else None
    bench_accessories = config["bench_accessories"] if "bench_accessories" in config else None
    deadlift_accessories = config["deadlift_accessories"] if "deadlift_accessories" in config else None
    ohp_accessories = config["ohp_accessories"] if "ohp_accessories" in config else None

    h.create_or_update_routine(api_key, routines, "Squat Day", folder_id, squats, squat_accessories)
    h.create_or_update_routine(api_key, routines, "Bench Day", folder_id, bench, bench_accessories)
    h.create_or_update_routine(api_key, routines, "Deadlift Day", folder_id, deads, deadlift_accessories)
    h.create_or_update_routine(api_key, routines, "OHP Day", folder_id, ohp, ohp_accessories)


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
    squats = a.generate_lifts(protocol, config["squat_tm"], ROUND_WEIGHT_PRECISION, False)
    bench = a.generate_lifts(protocol, config["bench_tm"], ROUND_WEIGHT_PRECISION, False)
    deads = a.generate_lifts(protocol, config["deadlift_tm"], ROUND_WEIGHT_PRECISION, True)
    ohp = a.generate_lifts(protocol, config["ohp_tm"], ROUND_WEIGHT_PRECISION, False)

    notes = f"Wave {wave}, Week {week}"

    setup_routines(
        api_key,
        config,
        [{"exercise_template_id": config["squat_exercise_id"], "sets": lifts_to_hevy_sets(squats), "notes": notes}],
        [{"exercise_template_id": config["bench_exercise_id"], "sets": lifts_to_hevy_sets(bench), "notes": notes}],
        [{"exercise_template_id": config["deadlift_exercise_id"], "sets": lifts_to_hevy_sets(deads), "notes": notes}],
        [{"exercise_template_id": config["ohp_exercise_id"], "sets": lifts_to_hevy_sets(ohp), "notes": notes}],
    )


def _compute_top_set_weight_kg(multiplier: float, training_max: float) -> float:
    """Compute the expected weight of the top set based on the multiplier and training max."""
    return u.lbs_to_kgs(a.round_weight(training_max * multiplier, ROUND_WEIGHT_PRECISION))


def _weights_equal(weight1: float, weight2: float) -> bool:
    """Compare two weights, allowing for small floating point differences."""
    return abs(weight1 - weight2) < 0.01


def _get_exercise_top_set_reps(exercise: h.HevyExercise, exercise_id: str, top_set_weight_kgs: float) -> int | None:
    """Search within an exercise for a top set that matches the expected weight."""
    if exercise["exercise_template_id"] == exercise_id:
        sets = exercise["sets"]
        if _weights_equal(sets[-1]["weight_kg"], top_set_weight_kgs):
            return sets[-1]["reps"]
    return None


def find_week3_top_sets_reps(config: c.Config, multiplier: float, workouts: list[h.HevyWorkout]) -> dict[str, int]:
    """Finds the top set for each main lift in wave 3 by searching backwards in training history.
    The way we find that is to search for a top set that matches algo.TEMPLATE[wave][3][last_element]. This is
    obviously not foolproof because if the user has changed the protocol, we won't find it.

    returns:
        A dictionary with keys "squat", "bench", "deadlift", "ohp" and values are the reps of the top set
    """
    squat_exercise_id = config["squat_exercise_id"]
    bench_exercise_id = config["bench_exercise_id"]
    deadlift_exercise_id = config["deadlift_exercise_id"]
    ohp_exercise_id = config["ohp_exercise_id"]

    squat_top_set_weight_kgs = _compute_top_set_weight_kg(multiplier, config["squat_tm"])
    bench_top_set_weight_kgs = _compute_top_set_weight_kg(multiplier, config["bench_tm"])
    deadlift_top_set_weight_kgs = _compute_top_set_weight_kg(multiplier, config["deadlift_tm"])
    ohp_top_set_weight_kgs = _compute_top_set_weight_kg(multiplier, config["ohp_tm"])

    logger.debug(f"Looking for Squat top set with weight {squat_top_set_weight_kgs} kg")
    logger.debug(f"Looking for Bench top set with weight {bench_top_set_weight_kgs} kg")
    logger.debug(f"Looking for Deadlift top set with weight {deadlift_top_set_weight_kgs} kg")
    logger.debug(f"Looking for OHP top set with weight {ohp_top_set_weight_kgs} kg")

    squat_top_set = None
    bench_top_set = None
    deadlift_top_set = None
    ohp_top_set = None
    for workout in workouts:
        for exercise in workout["exercises"]:
            if not squat_top_set:
                squat_top_set = _get_exercise_top_set_reps(exercise, squat_exercise_id, squat_top_set_weight_kgs)
            if not bench_top_set:
                bench_top_set = _get_exercise_top_set_reps(exercise, bench_exercise_id, bench_top_set_weight_kgs)
            if not deadlift_top_set:
                deadlift_top_set = _get_exercise_top_set_reps(
                    exercise, deadlift_exercise_id, deadlift_top_set_weight_kgs
                )
            if not ohp_top_set:
                ohp_top_set = _get_exercise_top_set_reps(exercise, ohp_exercise_id, ohp_top_set_weight_kgs)

            if squat_top_set and bench_top_set and deadlift_top_set and ohp_top_set:
                break

    logger.debug(f"Squats: {squat_top_set}")
    logger.debug(f"Bench: {bench_top_set}")
    logger.debug(f"Deadlift: {deadlift_top_set}")
    logger.debug(f"OHP: {ohp_top_set}")
    if not squat_top_set or not bench_top_set or not deadlift_top_set or not ohp_top_set:
        raise RuntimeError("One or more top sets not found.")

    return {"squat": squat_top_set, "bench": bench_top_set, "deadlift": deadlift_top_set, "ohp": ohp_top_set}


def main() -> None:
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
    parser.add_argument("--config", type=str, default="config.json", help="Config file to use")

    args = parser.parse_args()
    config = c.load_config(args.config)
    api_key = config["api_key"]

    if args.command == "program":
        if not args.wave or not args.week:
            parser.error("Wave and week are required for program")
        setup_week(api_key, config, args.wave, args.week)
    elif args.command == "maxes":
        logger.info("Recomputing training maxes")
        workouts = h.get_workouts(api_key)
        multiplier = a.TEMPLATE[args.wave - 1][2][-1][0]
        top_set_reps = find_week3_top_sets_reps(config, multiplier, workouts)

        old_squat_tm = config["squat_tm"]
        squat_top_set_weight = a.round_weight(old_squat_tm * multiplier, ROUND_WEIGHT_PRECISION)

        old_bench_tm = config["bench_tm"]
        bench_top_set_weight = a.round_weight(old_bench_tm * multiplier, ROUND_WEIGHT_PRECISION)

        old_deadlift_tm = config["deadlift_tm"]
        deadlift_top_set_weight = a.round_weight(old_deadlift_tm * multiplier, ROUND_WEIGHT_PRECISION)

        old_ohp_tm = config["ohp_tm"]
        ohp_top_set_weight = a.round_weight(old_ohp_tm * multiplier, ROUND_WEIGHT_PRECISION)

        expected_reps = [10, 8, 5, 3][args.wave - 1]
        new_squat_tm = a.compute_new_training_max(
            old_squat_tm,
            squat_top_set_weight,
            expected_reps,
            top_set_reps["squat"],
            SQUAT_INCREMENT,
            ONE_REP_MAX_THRESHOLD,
        )
        new_bench_tm = a.compute_new_training_max(
            old_bench_tm,
            bench_top_set_weight,
            expected_reps,
            top_set_reps["bench"],
            BENCH_INCREMENT,
            ONE_REP_MAX_THRESHOLD,
        )
        new_deadlift_tm = a.compute_new_training_max(
            old_deadlift_tm,
            deadlift_top_set_weight,
            expected_reps,
            top_set_reps["deadlift"],
            DEADLIFT_INCREMENT,
            ONE_REP_MAX_THRESHOLD,
        )
        new_ohp_tm = a.compute_new_training_max(
            old_ohp_tm, ohp_top_set_weight, expected_reps, top_set_reps["ohp"], OHP_INCREMENT, ONE_REP_MAX_THRESHOLD
        )

        print("New Training Maxes:")
        print("-------------------")
        print(f"Squats: {old_squat_tm}\t-> {new_squat_tm}")
        print(f"Bench: {old_bench_tm}\t-> {new_bench_tm}")
        print(f"Deadlift: {old_deadlift_tm}\t-> {new_deadlift_tm}")
        print(f"OHP: {old_ohp_tm}\t-> {new_ohp_tm}")

        print("\n")
        print("To save these back to your config, please type SAVE.  To abort, hit enter.")
        answer = input("> ")

        if answer == "SAVE":
            print(f"Backing up {args.config} to {args.config}.bak and saving...")
            shutil.copyfile(args.config, f"{args.config}.bak")

            config["squat_tm"] = new_squat_tm
            config["bench_tm"] = new_bench_tm
            config["deadlift_tm"] = new_deadlift_tm
            config["ohp_tm"] = new_ohp_tm

            c.save_config(config, args.config)
        else:
            print("Aborting...")


if __name__ == "__main__":
    main()
