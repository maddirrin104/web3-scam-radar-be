from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db_session
from app.schemas import LogIn, LogOut
from app.models import AlertLog

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("", response_model=LogOut)
def create_log(body: LogIn, db: Session = Depends(get_db_session)):
    row = AlertLog(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return LogOut(**row.__dict__)

@router.get("")
def list_logs(limit: int = 50, db: Session = Depends(get_db_session)):
    rows = db.query(AlertLog).order_by(AlertLog.id.desc()).limit(limit).all()
    return [{
        "id": r.id,
        "created_at": r.created_at,
        "tab_domain": r.tab_domain,
        "chain_id": r.chain_id,
        "contract": r.contract,
        "selector": r.selector,
        "risk": r.risk,
        "verdict": r.verdict,
        "reason": r.reason,
    } for r in rows]