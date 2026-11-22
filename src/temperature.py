from datetime import UTC, datetime, timedelta

import httpx
import structlog
from fastapi import HTTPException

from config import config
from metrics import TEMPERATURE_GAUGE, TEMPERATURE_REQUEST_LATENCY

logger = structlog.get_logger()

async def fetch_temperature():
    """ fetches data about temperature including
      the average of all boxes, number of total bboxes and number of available bboxes
    Returns:
    
    
    """
    now = datetime.now(UTC)
    one_hour_ago = now - timedelta(hours = 1)
    with TEMPERATURE_REQUEST_LATENCY.time():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url = config.api_url ,
                    params = {
                        "bbox": "-180,-90,180,90",
                        "phenomenon": "Temperatur",
                        "format": "json",
                        "from-date": one_hour_ago.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
                        "to-date": now.strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
                        "download": "false"
                        },
                        timeout = 30.0
                        )
                logger.debug(
                    "opensensemap_raw_response",
                    status_code=response.status_code,
                    content_length=len(response.content),
                    body_preview=response.text[:250],
                    )
                avg_temp, total_count, temp_count = compute_temperature_stats(response)

        except ValueError as e:
            raise HTTPException(status_code = 500, detail = str(e)) from e

        # Update the system temperature metric
        TEMPERATURE_GAUGE.set(avg_temp)
        tmp_status = temperature_status(avg_temp)
        
        final_payload = {
            "average_temperature": avg_temp,
            "status": tmp_status,
            "timestamp": now.isoformat(),
            "total_boxes": total_count,
            "accessible_boxes": temp_count
            }

        logger.info("temperature_fetched", **final_payload)
        return final_payload

def compute_temperature_stats(api_response: httpx.Response) -> float:
    """calculates and returns the average temperature
        with the opensense API json response to """
    json_response = api_response.json()
    total_count = len(json_response)
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
    average = temp_sum / temp_count
    return average, total_count, temp_count

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
