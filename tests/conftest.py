""" Test fixtures """
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.main import app

@pytest.fixture
def client():
    """ returns the mock client object """
    return TestClient(app)
@pytest.fixture
def mock_sensor_data():
    """ 
        Testing the averaging of values using mock data
        Expected average: 22.522630037
    """
    mock = MagicMock()
    mock.json.return_value =  [
        {"value": "20.12345678"},
        {"value": "22.87654321"},
        {"value": "24.56789012"},]
    return mock
@pytest.fixture
def large_sensor_data():
    """thousands of (valid) sensors data all near 20.0"""
    mock = MagicMock()
    mock.json.return_value = [
        {"value": str(20.0 + (i % 3) * 0.1)}   # values: 20.0, 20.1, 20.2 repeating
        for i in range(10000)
    ]
    return mock
@pytest.fixture
def empty_sensor_data():
    """opensensemap returns no results"""
    mock = MagicMock()
    mock.json.return_value = []
    return mock
@pytest.fixture
def corrupt_sensor_data():
    """a sensor sends a non-numeric value"""
    mock = MagicMock()
    mock.json.return_value = [
        {"value": "20.123456780"},
        {"value": None},
        {"value": "24.56789012"},
    ]
    return mock


@pytest.fixture
def cold_temperature_data():
    """ Temperatures that average below 10.0 deg (Too Cold).
        Values: 5.5, 8.2, 4.3 -> Average: 6.0 """
    mock = MagicMock()
    mock.json.return_value = [
        {"value": "5.500000000"},
        {"value": "8.200000000"},
        {"value": "4.300000000"},
    ]
    return mock

@pytest.fixture
def good_temperature_data():
    """ Temperatures that average between 10.0 and 36.0 deg (Good).
        Values: 20.5, 25.0, 14.5 -> Average: 20.0 """
    mock = MagicMock()
    mock.json.return_value = [
        {"value": "20.500000000"},
        {"value": "25.000000000"},
        {"value": "14.500000000"},
    ]
    return mock

@pytest.fixture
def hot_temperature_data():
    """ Temperatures that average above 36.0 deg (Too Hot).
        Values: 38.5, 42.0, 39.5 -> Average: 40.0 """
    mock = MagicMock()
    mock.json.return_value = [
        {"value": "38.500000000"},
        {"value": "42.000000000"},
        {"value": "39.500000000"},
    ]
    return mock
