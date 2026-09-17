import os
import requests

YOCO_SECRET_KEY = os.getenv("YOCO_SECRET_KEY")
BASE_URL = "https://payments.yoco.com/api"


def create_checkout(amount, currency="ZAR", metadata=None):

    if not YOCO_SECRET_KEY:
        raise Exception("YOCO_SECRET_KEY is not set.")

    url = f"{BASE_URL}/checkouts"

    headers = {
        "Authorization": f"Bearer {YOCO_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "amount": int(amount * 100),
        "currency": currency,
        "successUrl": "https://example.com/payment-success",
        "cancelUrl": "https://example.com/payment-cancelled"
    }

    if metadata:
        payload["metadata"] = metadata

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    data = response.json()

    return {
        "checkout_id": data.get("id"),
        "checkout_url": data.get("redirectUrl"),
        "raw_response": data
    }

