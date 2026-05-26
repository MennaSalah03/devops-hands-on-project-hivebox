""" Integration testing for app """
from unittest.mock import patch
import re

MOCK_TARGET = "src.main.httpx.get"
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

def test_temperature_too_hot_status(client, hot_temperature_data):
    """ Tests that the endpoint shows the correct status on hot temperatures """
    with patch("src.main.httpx.get", return_value = hot_temperature_data):
        response = client.get("/temperature")
        assert response.json()["status"] == "Too Hot"

def test_temperature_good_status(client, good_temperature_data):
    """ Tests that the endpoint shows the correct status on good temperatures """
    with patch("src.main.httpx.get", return_value = good_temperature_data):
        response = client.get("/temperature")
        assert response.json()["status"] == "Good"

def test_temperature_too_cold_status(client, cold_temperature_data):
    """ Tests that the endpoint shows the correct status on cold temperatures """
    with patch("src.main.httpx.get", return_value = cold_temperature_data):
        response = client.get("/temperature")
        assert response.json()["status"] == "Too Cold"

# ================== metrics endpoint tests ==================
def test_metrics_endpoint_is_reachable(client):
    """ testing the metrics endpoint """
    assert client.get("/metrics").status_code == 200

def read_counter_metrics(metrics_text: str, counter_name: str, labels: str) -> float:
    """gets the counter metrics from the etrics """
    match = re.search(rf"{counter_name}\{{{labels}\}} (\d+\.?\d*)", metrics_text)
    return float(match.group(1)) if match else 0.0

def test_temperature_counter_increments(client, mock_sensor_data):
    """Hitting /temperature twice should increment the request counter by exactly 2.
    
    Prometheus counters are global — they accumulate across the whole test session.
    So we read the counter before and after, and assert the delta is 2.
    """

    before = read_counter_metrics(
        client.get("/metrics").text,
        "hivebox_http_requests_total",
        'endpoint="/temperature"'
    )

    with patch(MOCK_TARGET, return_value=mock_sensor_data):
        client.get("/temperature")
        client.get("/temperature")


    after = read_counter_metrics(
        client.get("/metrics").text,
        "hivebox_http_requests_total",
        'endpoint="/temperature"'
    )
    assert after - before == 2.0, f"Expected counter to grow by 2, grew by {after - before}"

def test_temperature_gauge_is_set_after_request(client, mock_sensor_data):
    """After a /temperature call, the gauge metric should reflect the average."""
    with patch(MOCK_TARGET, return_value=mock_sensor_data):
        client.get("/temperature")
    metrics = client.get("/metrics").text
    assert "hivebox_temperature_average_celsius" in metrics

def test_latency_summary_is_recorded(client, mock_sensor_data):
    """The Summary metric should appear in /metrics after a temperature request."""
    with patch(MOCK_TARGET, return_value=mock_sensor_data):
        client.get("/temperature")
    metrics = client.get("/metrics").text
    assert "hivebox_temperature_request_duration_in_seconds" in metrics
