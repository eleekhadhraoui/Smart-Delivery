from fastapi import FastAPI
import uuid
import requests
import time

from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI()
SERVICE_NAME = "order-service"

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

DAPR_PUBLISH_URL = "http://localhost:3500/v1.0/publish/pubsub/order.created"

@app.post("/orders")
def create_order(order: dict):
    event = {
        "order_id": str(uuid.uuid4()),
        "product": order.get("product"),
        "quantity": order.get("quantity"),
        "customer": order.get("customer")
    }

    requests.post(DAPR_PUBLISH_URL, json=event)
    return {"message": "Order created", "order_id": event["order_id"]}
