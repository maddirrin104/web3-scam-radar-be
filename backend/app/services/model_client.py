from __future__ import annotations
import os
from typing import Any, Dict, Optional
import httpx

MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://host.docker.internal:8000")
_TIMEOUT = httpx.Timeout(15.0, connect=5.0)

# Nếu service model yêu cầu API key riêng, thêm ở đây
MODEL_API_KEY = os.getenv("MODEL_API_KEY", None)

def _headers() -> dict:
    h = {"accept": "application/json", "content-type": "application/json"}
    if MODEL_API_KEY:
        h["authorization"] = f"Bearer {MODEL_API_KEY}"
    return h

async def model_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forward payload tới /predict của service model.
    Payload chính là JSON mà script test của bạn đã gửi (account_address, transaction_history, explain flags...).
    """
    url = f"{MODEL_BASE_URL.rstrip('/')}/predict"
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_headers()) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

async def model_health() -> bool:
    try:
        url = f"{MODEL_BASE_URL.rstrip('/')}/health"
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_headers()) as client:
            r = await client.get(url)
            return r.status_code == 200
    except Exception:
        return False
