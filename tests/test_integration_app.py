""" Integration testing for app """
import json
import re
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from src.main import run_fetch_and_store_cycle


# ================== Root status check ==================
def test_root(client):
    """ Test the response of API root endpoint """
    response = client.get("/")
    assert response.status_code == 200
# ================== version endpoint tests ==================
def test_version(client):
    """ Test the response of version endpoint """
    response = client.get("/version")
    assert response.status_code == 200

def test_version_not_null(client):
    """ Test that the version at the endpoint isn't null """
    response = client.get("/version")
    assert response.json()["version"] is not None
    assert response.json()["version"] != ""
# def test_semver_format(client):
#     """ test for version being in the format v#.#.# """
#     response = client.get("/version")
#     version = response.json()["version"]
#     pattern = r"^v\d+\.+\d+\.+\d"
#     assert re.match(pattern, version), \
#         f"version {version} should match vX.X.X format."
# ================== temperature endpoint tests ==================
@patch("src.main.valkey_client.get", new_callable=AsyncMock)
def test_temperature_cache_hit(
    mock_valkey_get,
    client,
    ):
    """ If cache has data, return 200 and the parsed JSON payload. """
    expected_payload = {
        "average_temperature": 22.5,
        "status": "Good",
        "timestamp": datetime.now(tz=UTC).isoformat()
    }
    mock_valkey_get.return_value = json.dumps(expected_payload)

    response = client.get("/temperature")

    assert response.status_code == 200
    assert response.json() == expected_payload
    mock_valkey_get.assert_awaited_once_with("temperature")


@patch("src.main.valkey_client.get", new_callable=AsyncMock)
def test_temperature_cache_miss(
    mock_valkey_get,
    client,
    ):
    """ If cache has no, return 503. """
    mock_valkey_get.return_value = None

    response = client.get("/temperature")

    assert response.status_code == 503
    assert "detail" in response.json()
    mock_valkey_get.assert_awaited_once_with("temperature")
# ================== valkey and minIO tests ==================
@patch("src.main.httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("src.main.valkey_client.set", new_callable=AsyncMock)
@patch("src.main.Minio.put_object")
async def test_valkey_and_minio_save(
    mock_minio_put_object,
    mock_valkey_set,
    mock_httpx_get,
    mock_sensor_data
):
    """ Verify a successful fetch cycle writes valid JSON to both Valkey and MinIO """
    mock_httpx_get.return_value = mock_sensor_data

    await run_fetch_and_store_cycle()

    # inspect valkey
    mock_valkey_set.assert_awaited_once()
    valkey_args, valkey_kwargs = mock_valkey_set.call_args

    assert valkey_args[0] == "temperature"
    assert valkey_kwargs["ex"] == 300

    saved_cache_data = json.loads(valkey_args[1])

    assert round(saved_cache_data["average_temperature"], 9) == 22.522630037
    assert saved_cache_data["status"] == "Good"
    assert "timestamp" in saved_cache_data

    # inspect minio call
    mock_minio_put_object.assert_called_once()
    minio_kwargs = mock_minio_put_object.call_args.kwargs

    assert minio_kwargs["bucket_name"] == "hivebox-data"
    assert minio_kwargs["object_name"].startswith("temperature_")
    assert minio_kwargs["object_name"].endswith(".json")
    assert minio_kwargs["content_type"] == "application/json"

    minio_payload = json.loads(minio_kwargs["data"].getvalue().decode("utf-8"))
    assert minio_payload == saved_cache_data

# ================== metrics endpoint tests ==================
def test_metrics_endpoint_is_reachable(client):
    """ testing the metrics endpoint """
    assert client.get("/metrics").status_code == 200

def read_counter_metrics(metrics_text: str, counter_name: str, labels: str) -> float:
    """gets the counter metrics from the etrics """
    match = re.search(rf"{counter_name}\{{{labels}\}} (\d+\.?\d*)", metrics_text)
    return float(match.group(1)) if match else 0.0

@patch("src.main.valkey_client.get", new_callable=AsyncMock)
def test_temperature_counter_increments(
    mock_valkey_get,
    client,
    ):
    """Hitting cache twice should increment the request counter by exactly 2.
    
    Prometheus counters are global — they accumulate across the whole test session.
    So we read the counter before and after, and assert the delta is 2.
    """
    expected_payload = {
        "average_temperature": 22.5,
        "status": "Good",
        "timestamp": datetime.now(tz=UTC).isoformat()
    }
    mock_valkey_get.return_value = json.dumps(expected_payload)

    before = read_counter_metrics(
        client.get("/metrics").text,
        "hivebox_http_requests_total",
        'endpoint="/temperature"'
    )

    client.get("/temperature")
    client.get("/temperature")


    after = read_counter_metrics(
        client.get("/metrics").text,
        "hivebox_http_requests_total",
        'endpoint="/temperature"'
    )
    assert after - before == 2.0, f"Expected counter to grow by 2, grew by {after - before}"

@patch("src.main.valkey_client.get", new_callable=AsyncMock)
def test_temperature_gauge_is_set_after_request(
    mock_valkey_get,
    client):
    """After a /temperature call, the gauge metric should reflect the average."""
    expected_payload = {
        "average_temperature": 22.5,
        "status": "Good",
        "timestamp": datetime.now(tz=UTC).isoformat()
    }
    mock_valkey_get.return_value = json.dumps(expected_payload)

    client.get("/temperature")
    metrics = client.get("/metrics").text

    assert "hivebox_temperature_average_celsius" in metrics

@patch("src.main.valkey_client.get", new_callable=AsyncMock)
def test_latency_summary_is_recorded(
    mock_valkey_get,
    client,
    ):
    """The Summary metric should appear in /metrics after a temperature request."""
    expected_payload = {
        "average_temperature": 22.5,
        "status": "Good",
        "timestamp": datetime.now(tz=UTC).isoformat()
    }
    mock_valkey_get.return_value = json.dumps(expected_payload)

    client.get("/temperature")
    metrics = client.get("/metrics").text

    assert "hivebox_temperature_request_duration_in_seconds" in metrics
