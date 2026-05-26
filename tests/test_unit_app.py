""" unit tests for app """
from unittest.mock import MagicMock
import pytest
from src.main import get_avg_temp, temperature_status

# ================== temperature calculation ==================
def test_calculates_correct_average(mock_sensor_data):
    """Happy path: all valid floats, correct average returned."""
    result = get_avg_temp(mock_sensor_data)
    assert round(result, 9) == 22.522630037
def test_ignores_non_float_values(corrupt_sensor_data):
    """Corrupt values (strings, None) are skipped; average of valid ones returned."""
    result = get_avg_temp(corrupt_sensor_data)
    assert round(result, 9) == 22.34567345
def test_raises_on_empty_list(empty_sensor_data):
    """No valid readings should raise ValueError, not silently return 0."""
    with pytest.raises(ValueError, match="no valid temperature readings found"):
        get_avg_temp(empty_sensor_data)
def test_single_valid_reading():
    """Edge case: a single sensor should return exactly that sensor's value."""
    mock = MagicMock()
    mock.json.return_value = [{"value": "25.0"}]
    assert get_avg_temp(mock) == 25.0
def test_large_dataset_precision(large_sensor_data):
    """500 readings: result should match manually calculated average."""
    values = [float(s["value"]) for s in large_sensor_data.json()]
    expected = sum(values) / len(values)
    assert round(get_avg_temp(large_sensor_data), 5) == round(expected, 5)
def test_missing_value_key_is_skipped():
    """Sensors without a 'value' key entirely should not crash — just be skipped."""
    mock = MagicMock()
    mock.json.return_value = [{"sensor_id": "abc"}, {"value": "20.0"}]
    assert get_avg_temp(mock) == 20.0
def test_all_corrupt_raises():
    """If every reading is bad, should raise ValueError."""
    mock = MagicMock()
    mock.json.return_value = [{"value": "bad"}, {"value": None}, {"value": "???"}]
    with pytest.raises(ValueError):
        get_avg_temp(mock)
# ================== temperature status tests ==================
def test_returns_too_cold_below_10():
    """ Test withing the cold range """
    assert temperature_status(5.0) == "Too Cold"

def test_returns_too_cold_at_exact_boundary():
    """10.0 is the boundary — should still be Too Cold (<=10)."""
    assert temperature_status(10.0) == "Too Cold"

def test_returns_good_just_above_10():
    """10.001 is just above the lower boundary."""
    assert temperature_status(10.001) == "Good"

def test_returns_good_mid_range():
    """ test a temperature within Good range """
    assert temperature_status(22.0) == "Good"

def test_returns_good_at_upper_boundary():
    """36.0 is still within Good range (<=36)."""
    assert temperature_status(36.0) == "Good"

def test_returns_too_hot_above_36():
    """ Test withing too hot range """
    assert temperature_status(36.001) == "Too Hot"

def test_returns_too_hot_extreme():
    """ Test withing too hot range """
    assert temperature_status(100.0) == "Too Hot"

def test_returns_too_cold_negative():
    """Sub-zero temperatures should be Too Cold."""
    assert temperature_status(-5.0) == "Too Cold"
