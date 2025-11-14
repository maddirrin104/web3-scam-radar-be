from sqlalchemy.orm import Session
from app.models import Rule, DomainReputation, ContractReputation, FourByteSelector
from app.utils.text import extract_domain
from app.utils.crypto import is_evm_address, hex_selector
from .rules import RuleHit, level_from_score
from typing import Dict, Any, List

DEFAULT_RULES = {
    "DOMAIN_YOUNG_OR_SUSPICIOUS": 15,
    "HOMOGLYPH_OR_TYPO": 20,
    "APPROVE_INFINITY": 35,
    "SET_APPROVAL_FOR_ALL": 30,
    "PERMIT2": 25,
    "NON_VERIFIED_CONTRACT": 20,
}

SUSPICIOUS_SELECTORS = {
    # 4byte selectors (examples)
    "0x095ea7b3": ("approve(address,uint256)", "APPROVE_INFINITY"),
    "0xa22cb465": ("setApprovalForAll(address,bool)", "SET_APPROVAL_FOR_ALL"),
    # PERMIT2 common (simplified)
    "0x8fcbaf0c": ("permit(address,address,uint160,uint48,uint48,bool)", "PERMIT2"),
}

def load_rule_weight(db: Session, code: str) -> int:
    r = db.query(Rule).filter(Rule.code == code, Rule.enabled == True).first()
    if r:
        return r.weight
    return DEFAULT_RULES.get(code, 0)

def score_url(db: Session, url: str) -> dict:
    domain = extract_domain(url)
    reasons: List[str] = []
    score = 0

    rep = db.query(DomainReputation).filter(DomainReputation.domain == domain).first()
    if rep:
        score += rep.risk
        if rep.labels:
            reasons.append(f"domain_labels:{','.join(rep.labels.keys())}")

    # Example heuristic: homoglyph/typo (very naive placeholder)
    if any(c in domain for c in ["𝖊", "е", "ɾ", "Ｘ", "₿", "—", "-"]):
        w = load_rule_weight(db, "HOMOGLYPH_OR_TYPO")
        score += w
        reasons.append("homoglyph_or_typo")

    level = level_from_score(score)
    return {"risk": score, "level": level, "reasons": reasons, "labels": rep.labels if rep else {}}

def score_tx(db: Session, chain_id: int, to: str, data: str | None, value) -> dict:
    reasons: List[str] = []
    score = 0

    sel = hex_selector(data)
    if sel in SUSPICIOUS_SELECTORS:
        signature, rule_code = SUSPICIOUS_SELECTORS[sel]
        w = load_rule_weight(db, rule_code)
        score += w
        reasons.append(f"selector:{signature}")

    # Contract reputation
    crep = db.query(ContractReputation).filter(
        ContractReputation.chain_id == chain_id,
        ContractReputation.address == (to or "").lower()
    ).first()
    if crep:
        score += crep.risk
        if not crep.verified:
            w = load_rule_weight(db, "NON_VERIFIED_CONTRACT")
            score += w
            reasons.append("non_verified_contract")

    # Approve infinity quick check (very simplified: detects if calldata contains uint256 max)
    if sel == "0x095ea7b3" and ("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" in (data or "").lower()):
        w = load_rule_weight(db, "APPROVE_INFINITY")
        score += w
        reasons.append("approve_infinity")

    level = level_from_score(score)
    labels = (crep.labels if crep else {})
    return {"risk": score, "level": level, "reasons": reasons, "labels": labels}

from app.services.model_client import model_predict

async def score_tx_with_model(db, chain_id, to, data, value, context: dict | None = None):
    """
    context có thể chứa:
    - account_address
    - transaction_history (list) giống đúng format của team model
    - explain, explain_with_llm (bool)
    """
    # 1) Heuristic sẵn có
    heur = score_tx(db, chain_id, to, data, value)  # hàm cũ trả {risk, level, reasons, labels}
    score = heur["risk"]
    reasons = heur["reasons"]

    # 2) Gọi model nếu có context đầy đủ
    if context:
        try:
            resp = await model_predict(context)
            m_acc = float(resp.get("account_scam_probability", 0.0)) * 100
            m_tx  = float(resp.get("transaction_scam_probability", 0.0)) * 100
            mscore = max(m_acc, m_tx)

            # blend
            blended = int(0.6 * score + 0.4 * mscore)
            score = max(score, blended)  # hoặc lấy blended trực tiếp
            reasons.append("ml_blend")

            # bạn có thể đính kèm SHAP/LLM vào labels để FE hiển thị
            heur["labels"]["ml_raw"] = {
                "account_scam_probability": resp.get("account_scam_probability"),
                "transaction_scam_probability": resp.get("transaction_scam_probability"),
            }
            if "llm_explanation" in resp:
                heur["labels"]["llm_explanation"] = resp["llm_explanation"]

        except Exception as e:
            reasons.append(f"ml_call_failed:{e}")

    heur["risk"] = score
    heur["level"] = level_from_score(score)  # dùng helper cũ
    heur["reasons"] = reasons
    return heur
