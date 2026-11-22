from prometheus_client import Counter, Gauge, Summary, make_asgi_app

TEMPERATURE_GAUGE = Gauge(
    "hivebox_temperature_average_celsius",
    "The most recent average temperature fetched from openSenseMap"
)

TEMPERATURE_REQUEST_LATENCY = Summary(
    "hivebox_temperature_request_duration_in_seconds",
    "Time spent getting and processing temperature data from all sense boxes"
)

CACHE_HIT_COUNT = Counter(
    "hivebox_cache_hits_total",
    "Total number of /temperature cache hits",
    ["endpoint"]
)

metrics_app = make_asgi_app()