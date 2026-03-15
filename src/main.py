""" Hivebox's API Application using Fastapi """

from print_version import version_getter
from datetime import datetime, timezone, timedelta
import httpx
from fastapi import FastAPI


app = FastAPI()

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
@app.get("/temperature")
async def temperature():
    """Gets the temperature data from the opensensemap api"""
    api_url = "https://api.opensensemap.org/boxes/data"
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours = 1)
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
    return {"average_temperature": avg_temp}

def get_avg_temp(api_response):
    """calculates and returns the average temperature
        with the opensense API json response to"""
    json_response = api_response.json()
    temp_sum = 0
    temp_count = len(json_response)
    for sensor_idx in range(temp_count):
        temp = float(json_response[sensor_idx]["value"])
        temp_sum += temp
    average_temperature = temp_sum / temp_count
    return average_temperature
