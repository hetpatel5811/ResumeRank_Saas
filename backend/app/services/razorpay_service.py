import base64
import hashlib
import hmac
import json
from urllib import error, request

from fastapi import HTTPException, status

from app.config import settings


RAZORPAY_API_BASE = "https://api.razorpay.com/v1"


def _build_auth_header():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay is not configured yet. Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
        )

    token = f"{settings.RAZORPAY_KEY_ID}:{settings.RAZORPAY_KEY_SECRET}"
    encoded = base64.b64encode(token.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


def razorpay_api_request(method: str, endpoint: str, payload: dict | None = None):
    body = None
    headers = {
        "Authorization": _build_auth_header(),
        "Content-Type": "application/json",
    }

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url=f"{RAZORPAY_API_BASE}{endpoint}",
        data=body,
        headers=headers,
        method=method.upper(),
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
    except error.HTTPError as exc:
        response_text = exc.read().decode("utf-8")
        detail = "Razorpay request failed."

        try:
            parsed = json.loads(response_text)
            detail = parsed.get("error", {}).get("description") or detail
        except json.JSONDecodeError:
            if response_text:
                detail = response_text

        raise HTTPException(
            status_code=exc.code,
            detail=detail
        ) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach Razorpay. Please try again."
        ) from exc


def verify_razorpay_webhook_signature(raw_body: bytes, received_signature: str | None):
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Razorpay webhook secret is not configured."
        )

    if not received_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Razorpay signature header."
        )

    expected_signature = hmac.new(
        key=settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, received_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay webhook signature."
        )
