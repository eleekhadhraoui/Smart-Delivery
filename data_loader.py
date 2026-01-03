import requests
import random
import time
import uuid

PRODUCTS = [
    "Laptop", "Phone", "Tablet", "Headphones", "Smartwatch",
    "Monitor", "Keyboard", "Mouse", "Printer", "External Hard Drive"
]

CUSTOMERS = [
    "Ali", "Sara", "Omar", "Nour", "Yassine",
    "Hiba", "Mehdi", "Salma", "Karim", "Rania"
]

ORDER_URL = "http://localhost:8000/orders"

print("🚀 Starting real-time order traffic (Ctrl+C to stop)")

while True:
    order = {
        "product": random.choice(PRODUCTS),
        "quantity": random.randint(1, 5),
        "customer": random.choice(CUSTOMERS),
        "request_id": str(uuid.uuid4())
    }

    try:
        r = requests.post(ORDER_URL, json=order, timeout=3)
        print("Sent order:", order)
    except Exception as e:
        print("Error sending order:", e)

    # Random delay → simulates real users
    time.sleep(random.uniform(0.5, 2.5))
