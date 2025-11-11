from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List

class UrlScoreIn(BaseModel):
    url: HttpUrl

class TxScoreIn(BaseModel):
    chain_id: int
    to: str
    data: str | None = None # calldata hex
    value: str | int | None = None
    from_addr: Optional[str] = Field(None, alias="from")

class ScoreOut(BaseModel):
    risk: int
    level: str
    reasons: List[str] = []
    labels: Dict[str, Any] = {}

class ContractOut(BaseModel):
    chain_id: int
    address: str
    verified: bool
    risk: int
    labels: Dict[str, Any] = {}

class LogIn(BaseModel):
    tab_domain: str
    chain_id: int
    contract: str
    selector: str
    risk: int
    verdict: str
    reason: str
    raw: Dict[str, Any] = {}

class LogOut(LogIn):
    id: int