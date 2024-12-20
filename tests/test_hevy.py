"""Tests for hevy module."""


from juggy.hevy import lifts_to_hevy_sets


def test_lifts_to_hevy_sets_basic() -> None:
    """Test basic conversion of lifts to Hevy sets."""
    lifts: list[tuple[float | int, int] | None] = [(45, 5), (95, 3), None, (135, 5)]
    expected = [
        {"type": "warmup", "weight_kg": 20.41, "reps": 5},
        {"type": "warmup", "weight_kg": 43.09, "reps": 3},
        {"type": "normal", "weight_kg": 61.23, "reps": 5},
    ]
    result = lifts_to_hevy_sets(lifts)
    assert len(result) == len(expected)
    for actual, expect in zip(result, expected, strict=False):
        assert actual["type"] == expect["type"]
        assert round(actual["weight_kg"], 2) == expect["weight_kg"]
        assert actual["reps"] == expect["reps"]
