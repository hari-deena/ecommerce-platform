import hashlib
import hmac
from decimal import Decimal

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger(__name__)

RAZORPAY_API_BASE = "https://api.razorpay.com/v1"


class RazorpayClient:
    """Thin wrapper over the Razorpay REST API (kept dependency-free — plain
    httpx + basic auth — rather than pulling in the `razorpay` SDK)."""

    def __init__(self) -> None:
        self._auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
    async def create_order(self, *, amount: Decimal, currency: str, receipt: str) -> dict:
        """Amount must be in the smallest currency unit (paise for INR)."""
        payload = {
            "amount": int(amount * 100),
            "currency": currency,
            "receipt": receipt,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(
                    f"{RAZORPAY_API_BASE}/orders", json=payload, auth=self._auth
                )
                response.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("razorpay_create_order_failed", error=str(exc))
                raise ExternalServiceError("Could not initiate payment with Razorpay") from exc
        return response.json()

    def verify_signature(
        self, *, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str
    ) -> bool:
        body = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, razorpay_signature)

    def verify_webhook_signature(self, *, body: bytes, signature: str) -> bool:
        expected = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
