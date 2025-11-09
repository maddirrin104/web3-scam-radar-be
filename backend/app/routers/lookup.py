from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db_session
from app.schemas import ContractOut
from app.models import ContractReputation


router = APIRouter(prefix="/lookup", tags=["lookup"])


@router.get("/contract/{chain_id}/{address}", response_model=ContractOut)
def get_contract(chain_id: int, address: str, db: Session = Depends(get_db_session)):
rec = db.query(ContractReputation).filter(
ContractReputation.chain_id == chain_id,
ContractReputation.address == address.lower()
).first()
if not rec:
raise HTTPException(status_code=404, detail="Not found")
return ContractOut(
chain_id=rec.chain_id,
address=rec.address,
verified=rec.verified,
risk=rec.risk,
labels=rec.labels or {}
)