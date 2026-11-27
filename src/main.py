""" Hivebox's API Application using Fastapi """
import asyncio
import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

import httpx
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from config import config
from metrics import CACHE_HIT_COUNT, metrics_app
from services import minio_client, save_to_cache, save_to_storage, valkey_client
from temperature import fetch_temperature

logger = structlog.get_logger()

async def run_fetch_and_store_cycle():
    payload = await fetch_temperature()
    await save_to_cache(payload)
    save_to_storage(payload)

async def fetch_and_store_cycle():
    while True:
        try:
            await run_fetch_and_store_cycle()
        except Exception as e:
            logger.exception("unexpected_cycle_error", error=str(e))
        await asyncio.sleep(config.expiration_time) # 5 min.

@asynccontextmanager
async def lifespan(app: FastAPI):    
    bucket_name = config.minio_bucket

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        logger.info(f"Created MinIO bucket: {bucket_name}")

    task = asyncio.create_task(fetch_and_store_cycle())
    
    yield
    
    # SHUTDOWN
    task.cancel()
    await valkey_client.aclose()

app = FastAPI(lifespan=lifespan)
app.mount("/metrics", metrics_app)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/readyz")

@app.get("/readyz")
async def readiness_check():
    now = datetime.now(UTC)
    staleness_time = timedelta(seconds = float(2 * config.expiration_time))

    cached_raw = await valkey_client.get("temperature")
    if not cached_raw:
        raise HTTPException(status_code=503, detail="Cache is empty")

    # check cache freshness
    cached_data = json.loads(cached_raw)
    cache_age = now - datetime.fromisoformat(cached_data["timestamp"])

    if cache_age > staleness_time:
        raise HTTPException(status_code=503, detail="Cache is stale (> 2 cycles)")

    # check boxes availability
    total_boxes = cached_data.get("total_boxes", 0)
    accessible_boxes = cached_data.get("accessible_boxes", 0)
    if total_boxes == 0 or (total_boxes - accessible_boxes) >= (total_boxes // 2) + 1:
        raise HTTPException(status_code=503, detail="Majority of senseBoxes inaccessible")

    # Check MinIO storage freshness
    try:
        objects = list(minio_client.list_objects(config.minio_bucket, prefix="temperature_"))
        if not objects:
            raise HTTPException(status_code=503, detail="No stored data in MinIO")

        latest_obj = max(objects, key=lambda obj: obj.last_modified)
        storage_age = now - latest_obj.last_modified
        if storage_age > staleness_time:
            raise HTTPException(status_code=503, detail="Stored data is stale (> 2 cycles)")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MinIO check failed: {e}") from e

    return {"status": "ready"}

@app.post("/cache")
async def update_cache():
    try:
        payload = await fetch_temperature()
        await save_to_cache(payload)
        return {"message": "Cache updated", "data": payload}
    except (ValueError, httpx.HTTPError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# App Version Endpoint
@app.get(
        "/version",
        description = "gets the current app version (SemVer tag, commit SHA, or 'dev')",
        response_class = JSONResponse
        )
async def version():
    """Returns the current version of the app."""
    return {"version": config.app_version}

# Temperature Enpoint
@app.get(
        "/temperature",
        description = "shows average temperature and status for all senseboxes the were updated at most 1 hour from time of request",
        response_class = JSONResponse
        )
async def temperature():
    """Gets the temperature data from the opensensemap api"""
    CACHE_HIT_COUNT.labels(endpoint="/temperature").inc()

    cached_data = await valkey_client.get("temperature")
    if cached_data:
        return json.loads(cached_data)
    
    raise HTTPException(
        status_code=503,
        detail="Temperature data is initializing, please try again in a few seconds.")

@app.post("/store")
async def store_data():
    try:
        payload = await fetch_temperature()
        save_to_storage(payload)
        return {"message": "Data stored in MinIO", "data": payload}
    except (ValueError, httpx.HTTPError) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
