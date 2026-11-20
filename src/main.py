""" Hivebox's API Application using Fastapi """

import asyncio
import io
import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import httpx
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from minio import Minio
from prometheus_client import Counter, Gauge, Summary, make_asgi_app

from config import config
from print_version import version_getter

metrics_app = make_asgi_app()

# Setting up the metrics targets
TEMPERATURE_REQUEST_COUNTER = Counter(
    "hivebox_http_requests_total",
    "Total number of HTTP requests processed, labeled by endpoint",
    ["endpoint"],
)

TEMPERATURE_GAUGE = Gauge(
    "hivebox_temperature_average_celsius",
    "The most recent average temperature fetched from openSenseMap"
)

TEMPERATURE_REQUEST_LATENCY = Summary(
    "hivebox_temperature_request_duration_in_seconds",
    "Time spent getting and processing temperature data from all sense boxes"
)

valkey_client = redis.from_url(config.valkey_url, decode_responses=True)

minio_client = Minio(
    config.minio_endpoint,
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key,
    secure=False  # HTTP
)

async def run_fetch_and_store_cycle():
    now = datetime.now(UTC)
    one_hour_ago = now - timedelta(hours = 1)
    with TEMPERATURE_REQUEST_LATENCY.time():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url = config.api_url , params = {
                "bbox": "-180,-90,180,90",
                "phenomenon": "Temperatur",
                "format": "json",
                "from-date": one_hour_ago.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
                "to-date": now.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
                "download": "false"
                },
                timeout = 30.0)
                avg_temp = get_avg_temp(response)
        except ValueError as e:
            raise HTTPException(status_code = 500, detail = str(e)) from e

        # Update the system temperature metric
        TEMPERATURE_GAUGE.set(avg_temp)
        tmp_status = temperature_status(avg_temp)
        
        final_payload = {
            "average_temperature": avg_temp,
            "status": tmp_status,
            "timestamp": now.isoformat()
            }
        json_string = json.dumps(final_payload)
        
        # Save to Valkey
        await valkey_client.set("temperature", json_string, ex=300)

        byte_stream = io.BytesIO(json_string.encode("utf-8"))
        object_name = f"temperature_{final_payload['timestamp']}.json"

        # save to MinIO bucket
        minio_client.put_object(
            bucket_name="hivebox-data",
            object_name=object_name,
            data=byte_stream,
            length=len(json_string.encode("utf-8")),
            content_type="application/json"
        )


async def fetch_and_store_cycle():
    while True:
        await fetch_and_store_cycle()
        await asyncio.sleep(300) # 5 min.


@asynccontextmanager
async def lifespan(app: FastAPI):    
    bucket_name = config.minio_bucket

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Created MinIO bucket: {bucket_name}")

    task = asyncio.create_task(fetch_and_store_cycle())
    
    yield
    
    # SHUTDOWN
    task.cancel()
    await valkey_client.aclose()

app = FastAPI(lifespan=lifespan)
app.mount("/metrics", metrics_app)

@app.get("/")
async def root():
    """The API's root"""
    return {"message": "welcome to the hivebox API"}

# App Version Endpoint
@app.get(
        "/version",
        description = "gets the current app version in the SemVer form vx.x.x",
        response_class = JSONResponse
        )
async def version():
    """Gets the version of the app to the API"""
    return {"version": str(version_getter("version.txt"))}

# Temperature Enpoint
@app.get(
        "/temperature",
        description = "shows average temperature and status for all senseboxes the were updated at most 1 hour from time of request",
        response_class = JSONResponse
        )
async def temperature():
    """Gets the temperature data from the opensensemap api"""
    TEMPERATURE_REQUEST_COUNTER.labels(endpoint="/temperature").inc()

    cached_data = await valkey_client.get("temperature")
    if cached_data:
        return json.loads(cached_data)
    
    raise HTTPException(
        status_code=503,
        detail="Temperature data is initializing, please try again in a few seconds.")

def get_avg_temp(api_response: dict) -> float:
    """calculates and returns the average temperature
        with the opensense API json response to """
    json_response = api_response.json()
    temp_sum = 0
    temp_count = 0
    for sensor in json_response:
        try:
            temp_sum += float(sensor["value"])
            temp_count += 1
        except (ValueError, TypeError, KeyError):
            continue # ignore other types than float
    if temp_count == 0:
        raise ValueError("no valid temperature readings found")
    return temp_sum / temp_count

def temperature_status(average_temperature: float) -> str:
    """ Returns the status of temperature according to the range it belongs to.
        Less than 10 deg.: too cold
        Between 10 adn 36 deg.: Good
        Higher than 36: Too hot
        """
    if average_temperature <= 10.0:
        return "Too Cold"
    elif average_temperature > 10.0 and average_temperature <= 36.0:
        return "Good"
    elif average_temperature > 36.0:
        return "Too Hot"
