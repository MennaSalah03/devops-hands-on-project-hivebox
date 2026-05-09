""" Hivebox's API Application using Fastapi """

from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException
import httpx
from prometheus_client import Counter, Gauge, make_asgi_app
from print_version import version_getter


app = FastAPI()
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

REQUEST_COUNTER = Counter(
    "app_requests_total",
    "Total number of requests to the app",
    ["endpoint"],
)

RANDOMM_NUMBER_GAUGE = Gauge(
    "App random number",
    "Current value of random number"
)


# API's root
@app.get("/")
async def root():
    """The API's root"""
    return {"message": "welcome to the hivebox API"}

# App Version Endpoint
@app.get("/version")
async def version():
    """Gets the version of the app to the API"""
    return {"version": str(version_getter("version.txt"))}

# Temperature Enpoint
@app.get("/temperature", description = "shows average temperature and status for all senseboxes data")
async def temperature():
    """Gets the temperature data from the opensensemap api"""
    api_url = "https://api.opensensemap.org/boxes/data"
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours = 1)
    try:
        response = httpx.get(url = api_url , params = {
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
    tmp_status = temperature_status(avg_temp)
    return {"average_temperature": avg_temp, "status": tmp_status}

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
    elif average_temperature > 10.0 or average_temperature <= 36.0:
        return "Good"
    elif average_temperature > 36.0:
        return "Too Hot"
