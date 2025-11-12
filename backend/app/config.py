from pydantic import BaseModel
import os
import json

class Settings(BaseModel):
    api_title: str = os.getenv("API_TITLE", "ScamRadar Backend")
    api_version: str = os.getenv("API_VERSION", "0.1.0")
    api_debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    database_url: str = os.getenv("DATABASE_URL")
    policy_etag: str = os.getenv("POLICY_ETAG", "v1")
    etherscan_keys: list[str] = []
    rarible_api_key: str = os.getenv("RARIBLE_API_KEY", "")
settings = Settings()

raw_keys = os.getenv("API_KEYS")
if raw_keys:
    try:
        settings.etherscan_keys = json.loads(raw_keys)
    except Exception:
        # fallback: comma-separated
        settings.etherscan_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]