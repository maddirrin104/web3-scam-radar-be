from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import UrlScoreIn, TxScoreIn, ScoreOut
from app.deps import get_db_session
from app.risk.engine import score_url, score_tx

router = APIRouter(prefix="/score", tags=["score"])

@router.post("/url", response_model=ScoreOut)
def score_url_ep(body: UrlScoreIn, db: Session = Depends(get_db_session)):
    res = score_url(db, body.url)
    return ScoreOut(**res)

@router.post("/tx", response_model=ScoreOut)
def score_tx_ep(body: TxScoreIn, db: Session = Depends(get_db_session)):
    res = score_tx(db, body.chain_id, (body.to or "").lower(), body.data, body.value)
    return ScoreOut(**res)