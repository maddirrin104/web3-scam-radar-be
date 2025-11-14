from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.orchestrators.detector import detect_account_or_tx

router = APIRouter(prefix="/detect", tags=["detect"])

class DetectIn(BaseModel):
    account_address: str = Field(..., description="EOA hoặc contract address")
    tx_hash: Optional[str] = Field(None, description="Tx hash nếu muốn kiểm tra 1 giao dịch cụ thể")
    explain: bool = False
    explain_with_llm: bool = False

@router.post("")
async def detect(body: DetectIn):
    try:
        res = await detect_account_or_tx(
            account_address=body.account_address,
            tx_hash=body.tx_hash,
            explain=body.explain,
            explain_with_llm=body.explain_with_llm,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"detect failed: {e}")
