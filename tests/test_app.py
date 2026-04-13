""" unit tests for app """
from unittest.mock import patch
import re
from src.main import get_avg_temp

# ================== Endpoints status checks ==================
def test_root(client):
    """ Test the response of API root endpoint """
    response = client.get("/")
    assert response.status_code == 200

def test_version(client):
    """ Test the response of version endpoint """
    response = client.get("/version")
    assert response.status_code == 200

def test_temperature_endpoint(client, mock_sensor_data):
    """ Test the reponse of temperature endpoint """
    with patch("src.main.httpx.get", return_value = mock_sensor_data):
        response = client.get("/temperature")
        assert response.status_code == 200

# ================== version endpoint tests ==================
def test_version_not_null(client):
    """ Test that the version at the endpoint isn't null """
    response = client.get("/version")
    assert response.json()["version"] is not None
    assert response.json()["version"] != ""
def test_semver_format(client):
    """ test for version being in the format v#.#.# """
    response = client.get("/version")
    version = response.json()["version"]
    pattern = r"^v\d+\.+\d+\.+\d"
    assert re.match(pattern, version), \
        f"version {version} should match vX.X.X format."
# ================== temperature endpoint tests ==================


def test_average_temperature(client, mock_sensor_data):
    """ test the averaging of the temperatures is correct
        for this testcase and mock data, the average should be 22.0"""
    with patch("src.main.httpx.get", return_value = mock_sensor_data):
        response = client.get("/temperature")
        assert round(response.json()["average_temperature"], 9) == 22.522630037

def test_get_avg_temp_calculates_correctly(mock_sensor_data, corrupt_sensor_data):
    """ Tests that the average we get is correct even with corrupt data """
    invalid_data_result = get_avg_temp(corrupt_sensor_data)
    valid_data_result = get_avg_temp(mock_sensor_data)
    assert round(invalid_data_result, 9) == 22.34567345
    assert round(valid_data_result, 9) == 22.522630037

def test_temperature_corrupt_data_is_handled(client, corrupt_sensor_data):
    """ testing the case when a sensor sending data instead of a float.
    Not filtering non-float numbers would cause the test to fail. """
    with patch("src.main.httpx.get", return_value = corrupt_sensor_data):
        response = client.get("/temperature")
        assert response.status_code == 200

def test_temperature_empty_data_not_accepted(client, empty_sensor_data):
    """ Testing of when empty data list is sent """
    with patch("src.main.httpx.get", return_value = empty_sensor_data):
        response = client.get("/temperature")
        assert response.status_code == 500

def test_temperature_huge_amount_of_sensor_data(client, large_sensor_data):
    """ Tests the temperature endpoint with a large input from the sensors """
    with patch("src.main.httpx.get", return_value = large_sensor_data):
        response = client.get("/temperature")
    values = [float(s["value"]) for s in large_sensor_data.json()]
    expected_avg = sum(values) / len(values)
    assert round(response.json()["average_temperature"], 5) == round(expected_avg, 5)
