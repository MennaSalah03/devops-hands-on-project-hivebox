import io
import json

import redis.asyncio as redis
from minio import Minio

from config import config

valkey_client = redis.from_url(config.valkey_url, decode_responses=True)

minio_client = Minio(
    config.minio_endpoint,
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key,
    secure=False  # HTTP
)

async def save_to_cache(payload: dict) -> None:
    json_string = json.dumps(payload)
    await valkey_client.set("temperature", json_string, ex=config.expiration_time)


# save to MinIO bucket
def save_to_storage(payload: dict) -> None:
    json_string = json.dumps(payload)
    byte_stream = io.BytesIO(json_string.encode("utf-8"))
    object_name = f"temperature_{payload['timestamp']}.json"

    minio_client.put_object(
        bucket_name="hivebox-data",
        object_name=object_name,
        data=byte_stream,
        length=len(json_string.encode("utf-8")),
        content_type="application/json"
    )

