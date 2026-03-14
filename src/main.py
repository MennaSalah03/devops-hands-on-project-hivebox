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
    api_url = "https://api.opensensemap.org/boxes/"
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours = 1)
    response = httpx.get(url = api_url , params = {
        "bbox": "-180,-90,180,90",
        "phenomenon": "Temperatur",
        "format": "json",
        "from-date": one_hour_ago.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
        "to-date": now.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
        "download": "false",
        "operation": "arithmeticMean",
        "window": "1h"
        })
    return response.json()
