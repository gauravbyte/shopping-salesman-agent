from __future__ import annotations
"""
Pine Labs PinePG payment service.

Wraps the five core APIs:
  1. generate_token        — cached Bearer token
  2. hosted_checkout_create — create checkout session, get redirect_url
  3. get_order_status      — poll payment status
  4. cancel_order          — void an unpaid order
  5. create_refund         — refund a captured payment
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import requests

from ..core.config import settings

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


# Simple in-memory token cache
_cached_token: str = ""
_token_expires_at: datetime = datetime.min.replace(tzinfo=timezone.utc)

_JSON_HEADERS = {"accept": "application/json", "content-type": "application/json"}
_BASIC_HEADERS = {"accept": "application/json"}


def _request(method: str, path: str, *, auth: bool = True, **kwargs) -> dict:
    url = f"{settings.PINE_LABS_BASE_URL}{path}"
    headers: dict = kwargs.pop("headers", {})
    if auth:
        headers["Authorization"] = f"Bearer {_get_token()}"

    resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)

    if not resp.ok:
        try:
            detail = resp.json().get("error_message") or resp.json().get("message") or resp.text
        except Exception:
            detail = resp.text
        logger.error("PineLabs %s %s → %s: %s", method, path, resp.status_code, detail)
        raise PaymentError(resp.status_code, detail)

    try:
        return resp.json()
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# 1. Token (OAuth2 client_credentials, cached until expiry)
# ---------------------------------------------------------------------------

def _get_token() -> str:
    global _cached_token, _token_expires_at
    now = datetime.now(timezone.utc)
    if _cached_token and now < _token_expires_at:
        return _cached_token

    data = _request(
        "POST", "/auth/v1/token",
        auth=False,
        json={
            "client_id": settings.PINE_LABS_CLIENT_ID,
            "client_secret": settings.PINE_LABS_CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        headers=_JSON_HEADERS.copy(),
    )

    _cached_token = data["access_token"]
    # Pine Labs returns expires_at as ISO string e.g. "2026-03-14T10:26:17.288Z"
    raw_exp = data.get("expires_at", "")
    try:
        exp = datetime.fromisoformat(raw_exp.replace("Z", "+00:00"))
        # Subtract 60s safety buffer
        _token_expires_at = exp.replace(second=max(0, exp.second - 60))
    except Exception:
        # Fallback: treat as valid for 1 hour
        from datetime import timedelta
        _token_expires_at = now + timedelta(hours=1)

    return _cached_token


# ---------------------------------------------------------------------------
# 2. Hosted Checkout
# ---------------------------------------------------------------------------

def hosted_checkout_create(
    *,
    merchant_order_reference: str,
    amount_paise: int,
    customer_email: str,
    customer_name: str,
    customer_mobile: str = "9999999999",
) -> dict:
    first, *rest = customer_name.split(" ", 1)
    last = rest[0] if rest else first

    payload = {
        "merchant_order_reference": merchant_order_reference,
        "order_amount": {"value": amount_paise, "currency": "INR"},
        "pre_auth": False,
        "purchase_details": {
            "customer": {
                "email_id": customer_email,
                "first_name": first,
                "last_name": last,
                "mobile_number": customer_mobile,
                "billing_address": {
                    "address1": "123 Main Street",
                    "pincode": "400001",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "IN",
                },
                "shipping_address": {
                    "address1": "123 Main Street",
                    "pincode": "400001",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "IN",
                },
            },
        },
        "callback_url": settings.PINE_LABS_RETURN_URL,
    }

    return _request("POST", "/checkout/v1/orders", json=payload, headers=_JSON_HEADERS.copy())


# ---------------------------------------------------------------------------
# 3. Get order status
# ---------------------------------------------------------------------------

def get_order_status(pine_labs_order_id: str) -> dict:
    return _request("GET", f"/pay/v1/orders/{pine_labs_order_id}", headers=_BASIC_HEADERS.copy())


# ---------------------------------------------------------------------------
# 4. Cancel order
# ---------------------------------------------------------------------------

def cancel_order(pine_labs_order_id: str) -> dict:
    return _request("PUT", f"/pay/v1/orders/{pine_labs_order_id}/cancel", headers=_BASIC_HEADERS.copy())


# ---------------------------------------------------------------------------
# 5. Create refund
# ---------------------------------------------------------------------------

def create_refund(pine_labs_order_id: str, amount_paise: int | None = None) -> dict:
    payload: dict[str, Any] = {}
    if amount_paise is not None:
        payload["refund_amount"] = {"value": amount_paise, "currency": "INR"}
    return _request("POST", f"/pay/v1/refunds/{pine_labs_order_id}", json=payload, headers=_JSON_HEADERS.copy())
