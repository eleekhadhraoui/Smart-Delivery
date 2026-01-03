from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
import time

app = FastAPI()
SERVICE_NAME = "tracking-service"
tracking = {}

# ---------- METRICS ----------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "HTTP Requests",
    ["service", "method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Latency",
    ["service", "endpoint"]
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)

    REQUEST_COUNT.labels(
        SERVICE_NAME,
        request.method,
        request.url.path,
        response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        SERVICE_NAME,
        request.url.path
    ).observe(time.time() - start)

    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
# --------------------------------

def extract_payload(event: dict) -> dict:
    return event.get("data", event)

@app.get("/dapr/subscribe")
def subscribe():
    return [
        {
            "pubsubname": "pubsub",
            "topic": "order.status.updated",
            "route": "/tracking"
        }
    ]

@app.post("/tracking")
def track(event: dict):
    payload = extract_payload(event)
    tracking.setdefault(payload["order_id"], []).append(payload["status"])
    return {"message": "Tracked"}
