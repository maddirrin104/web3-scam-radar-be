import itertools, httpx
from app.config import settings

_cycle = itertools.cycle(settings.etherscan_keys or [])

async def etherscan_get(module: str, action: str, **params):
    key = next(_cycle) if settings.etherscan_keys else ""
    q = {"module": module, "action": action, "apikey": key, **params}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get("https://api.etherscan.io/api", params=q)
        r.raise_for_status()
        return r.json()
