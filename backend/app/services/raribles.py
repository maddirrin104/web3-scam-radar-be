from __future__ import annotations
import os
from typing import Any, Dict, Optional
import httpx
from app.config import settings

BASE_URL = os.getenv("RARIBLE_BASE_URL", "https://api.rarible.org/v0.1")

RARIBLE_API_KEY = getattr(settings, "rarible_api_key", None) or os.getenv("RARIBLE_API_KEY", "")

HEADERS = {
    "accept": "application/json",
    "x-api-key": RARIBLE_API_KEY,
}

_DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

# --- Các hàm API cơ bản ---

async def rarible_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Gửi GET request đến Rarible API và trả về JSON đã parse.
    Sẽ báo lỗi httpx.HTTPStatusError nếu status code không phải 2xx.
    """
    if not RARIBLE_API_KEY:
        raise RuntimeError("RARIBLE_API_KEY chưa được thiết lập")

    url = f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT, headers=HEADERS) as client:
        r = await client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()


async def rarible_post(path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not RARIBLE_API_KEY:
        raise RuntimeError("RARIBLE_API_KEY chưa được thiết lập")

    url = f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT, headers=HEADERS) as client:
        r = await client.post(url, json=json or {})
        r.raise_for_status()
        return r.json()


# === Các hàm tiện ích (Convenience wrappers) ===
async def item_by_id(item_id: str) -> Dict[str, Any]:
    """Lấy item bằng ID đầy đủ, ví dụ: 'ETHEREUM:0x...:1234'."""
    return await rarible_get(f"items/{item_id}")

async def items_by_owner(
    owner: str,
    blockchain: str = "ETHEREUM",
    size: int = 20,
    continuation: Optional[str] = None,
) -> Dict[str, Any]:
    owner_full = f"{blockchain}:{owner}"
    params: Dict[str, Any] = {"owner": owner_full, "size": size}
    if continuation:
        params["continuation"] = continuation
    return await rarible_get("items/byOwner", params=params)

async def collection_by_id(collection_id: str) -> Dict[str, Any]:
    """Lấy collection bằng ID, ví dụ: 'ETHEREUM:0x...'."""
    return await rarible_get(f"collections/{collection_id}")

async def search_collections(
    text: str,
    blockchain: Optional[str] = None,
    size: int = 20,
    continuation: Optional[str] = None,
) -> Dict[str, Any]:
    """Tìm kiếm collection bằng từ khóa (text)."""
    params: Dict[str, Any] = {"text": text, "size": size}
    if blockchain:
        params["blockchain"] = blockchain
    if continuation:
        params["continuation"] = continuation
    return await rarible_get("collections/search", params=params)

async def rarible_health() -> bool:
    """Kiểm tra xem Rarible API có phản hồi hay không."""
    try:
        await rarible_get("status/ready")
        return True
    except Exception:
        return False