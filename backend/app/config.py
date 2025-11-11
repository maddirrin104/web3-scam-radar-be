from pydantic import BaseModel
import os

class Settings(BaseModel):
    api_title: str = os.getenv("API_TITLE", "ScamRadar Backend")
    api_version: str = os.getenv("API_VERSION", "0.1.0")
    api_debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    database_url: str = os.getenv("DATABASE_URL")
    policy_etag: str = os.getenv("POLICY_ETAG", "v1")

settings = Settings()