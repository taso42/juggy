"""Tests for the Juggernaut method algorithm."""

import pytest

from juggy.algo import DELOAD_WEEK, TEMPLATE, generate_lifts


def test_deload_week_structure():
    """Test that DELOAD_WEEK has the correct structure and values."""
    assert len(DELOAD_WEEK) == 3
    for ratio, reps in DELOAD_WEEK:
        assert isinstance(ratio, float)
        assert isinstance(reps, int)
        assert 0 < ratio <= 1.0
        assert reps > 0


def test_template_structure():
    """Test that TEMPLATE has the correct structure (4 waves, each with weeks and sets)."""
    assert len(TEMPLATE) == 4  # 4 waves

    for wave_idx, wave in enumerate(TEMPLATE, 1):
        assert len(wave) == 4, f"Wave {wave_idx} should have 4 weeks"
        
        for week_idx, week in enumerate(wave, 1):
            assert isinstance(week, list), f"Week {week_idx} in Wave {wave_idx} should be a list"
            
            for set_idx, (ratio, reps) in enumerate(week, 1):
                assert isinstance(ratio, float), f"Set {set_idx} ratio in Week {week_idx}, Wave {wave_idx} should be float"
                assert isinstance(reps, int), f"Set {set_idx} reps in Week {week_idx}, Wave {wave_idx} should be int"
                assert 0 < ratio <= 1.0, f"Set {set_idx} ratio in Week {week_idx}, Wave {wave_idx} should be between 0 and 1"
                assert reps > 0, f"Set {set_idx} reps in Week {week_idx}, Wave {wave_idx} should be positive"


@pytest.mark.parametrize("training_max,expected", [
    (100, [(40.0, 5), (50.0, 5), (60.0, 5)]),  # Test with 100 lbs
    (225, [(90.0, 5), (112.5, 5), (135.0, 5)]),  # Test with 225 lbs
])
def test_generate_lifts(training_max, expected):
    """Test generate_lifts with different training maxes."""
    result = generate_lifts(DELOAD_WEEK, training_max)
    assert len(result) == len(expected)
    
    for (actual_weight, actual_reps), (expected_weight, expected_reps) in zip(result, expected):
        assert actual_reps == expected_reps
        assert abs(actual_weight - expected_weight) < 0.1  # Allow small floating point differences


def test_generate_lifts_invalid_input():
    """Test generate_lifts with invalid inputs."""
    with pytest.raises(TypeError):
        generate_lifts("not a list", 100)
    
    with pytest.raises(TypeError):
        generate_lifts(DELOAD_WEEK, "not a number")
