from fastapi import APIRouter, HTTPException, Request
from app.services.model_client import model_predict

router = APIRouter(prefix="/ml", tags=["ml"])

@router.post("/predict")
async def proxy_predict(req: Request):
    """
    Proxy/minh bạch: nhận JSON rồi chuyển tiếp sang MODEL_BASE_URL/predict
    Trả nguyên JSON của model (account_scam_probability, transaction_scam_probability, shap_values, llm_explanation...)
    """
    try:
        payload = await req.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    try:
        result = await model_predict(payload)
        return result
    except Exception as e:
        # cố gắng lấy body lỗi để debug
        raise HTTPException(status_code=502, detail=f"Model service error: {e}")
