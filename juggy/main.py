"""Main application module."""
import argparse
import os

import dotenv

import juggy.algo as a
import juggy.config as c
import juggy.hevy as h


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

    h.setup_routines(
        api_key,
        f"Wave {wave}, Week {week}",
        [{"exercise_template_id": config["squat_exercise_id"], "sets": h.lifts_to_hevy_sets(squats), "notes": notes}],
        [{"exercise_template_id": config["bench_exercise_id"], "sets": h.lifts_to_hevy_sets(bench), "notes": notes}],
        [{"exercise_template_id": config["deadlift_exercise_id"], "sets": h.lifts_to_hevy_sets(deads), "notes": notes}],
        [{"exercise_template_id": config["ohp_exercise_id"], "sets": h.lifts_to_hevy_sets(ohp), "notes": notes}],
    )


def main() -> None:
    dotenv.load_dotenv()
    api_key = os.getenv("HEVY_API_KEY", "undefined")

    config = c.load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", type=int, required=True, help="The wave of the program (1-4)")
    parser.add_argument("--week", type=int, required=True, help="The week number of the program (1-4)")
    args = parser.parse_args()
    setup_week(api_key, config, args.wave, args.week)


if __name__ == "__main__":
    main()
