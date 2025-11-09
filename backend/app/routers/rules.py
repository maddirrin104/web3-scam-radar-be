from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db_session
from app.config import settings
from app.models import Rule, PolicySnapshot


router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("/snapshot")
def get_policy_snapshot(db: Session = Depends(get_db_session)):
snap = db.query(PolicySnapshot).filter(PolicySnapshot.etag == settings.policy_etag).first()
payload = snap.payload if snap else {"etag": settings.policy_etag, "rules": []}
return payload


@router.get("")
def list_rules(db: Session = Depends(get_db_session)):
rows = db.query(Rule).all()
return [{"code": r.code, "weight": r.weight, "enabled": r.enabled, "description": r.description} for r in rows]