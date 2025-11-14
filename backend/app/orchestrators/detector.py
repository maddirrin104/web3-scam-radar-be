from __future__ import annotations
from typing import Any, Dict, List, Optional
import math

from app.services.model_client import model_predict
from app.services.raribles import items_by_owner
from app.config import settings

import httpx
import itertools
from app.config import settings

# --- Etherscan helpers (dùng đúng vòng xoay key bạn đã có) ---
_cycle = itertools.cycle(settings.etherscan_keys or [])

async def _eth_proxy(action: str, **params) -> Dict[str, Any]:
    key = next(_cycle) if settings.etherscan_keys else ""
    q = {"module": "proxy", "action": action, "apikey": key, **params}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get("https://api.etherscan.io/api", params=q)
        r.raise_for_status()
        js = r.json()
        if js.get("result") in (None, "0x"):
            # Etherscan vẫn 200 nhưng result rỗng → coi như không có
            return {}
        return js

def _hex_to_int(x: Optional[str]) -> int:
    if not x:
        return 0
    try:
        return int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
    except Exception:
        return 0

# selector → tên hàm (rút gọn; bổ sung khi cần)
SIG_MAP = {
    "0x095ea7b3": "approve",
    "0xa22cb465": "setApprovalForAll",
    "0x8fcbaf0c": "permit",  # ví dụ
}

def _decode_function_names(input_data: Optional[str]) -> List[str]:
    if not input_data or len(input_data) < 10:
        return []
    sel = input_data[:10].lower()
    name = SIG_MAP.get(sel)
    return [name] if name else []

async def _build_tx_item_from_hash(tx_hash: str) -> Dict[str, Any]:
    """
    Lấy dữ liệu tx từ Etherscan (proxy API) và build 1 phần tử transaction_history
    theo đúng format model yêu cầu.
    """
    tx = await _eth_proxy("eth_getTransactionByHash", txhash=tx_hash)
    txr = await _eth_proxy("eth_getTransactionReceipt", txhash=tx_hash)

    tx_res = tx.get("result", {}) if tx else {}
    r_res  = txr.get("result", {}) if txr else {}

    # Lấy block để có timestamp (tuỳ chọn)
    ts = 0
    try:
        if tx_res.get("blockNumber"):
            blk = await _eth_proxy("eth_getBlockByNumber",
                                   tag=tx_res["blockNumber"], boolean="false")
            ts = _hex_to_int(blk.get("result", {}).get("timestamp"))
    except Exception:
        pass

    item = {
        "from_address": tx_res.get("from", "") or tx_res.get("from_address", ""),
        "to_address":   tx_res.get("to", "")   or tx_res.get("to_address", ""),
        "value": _hex_to_int(tx_res.get("value")),
        "gasPrice": _hex_to_int(tx_res.get("gasPrice")),
        "gasUsed": _hex_to_int(r_res.get("gasUsed")),
        "timestamp": ts,
        "function_call": _decode_function_names(tx_res.get("input")),
        # Các field NFT/market mặc định 0 (sẽ cố enrich bằng Rarible phía dưới)
        "token_value": 0,
        "nft_floor_price": 0,
        "nft_average_price": 0,
        "nft_total_volume": 0,
        "nft_total_sales": 0,
        "nft_num_owners": 0,
        "nft_market_cap": 0,
    }
    return item

async def _enrich_nft_metrics(account: str, tx_item: Dict[str, Any]) -> None:
    """
    Thử lấy vài chỉ số từ Rarible để lấp các trường NFT*. Đây là bản nhẹ:
    - Đếm item đang sở hữu làm proxy cho owners/sales (tối giản).
    Bạn có thể thay bằng API collection metrics riêng nếu có quyền.
    """
    try:
        owned = await items_by_owner(owner=account)
        total = int(owned.get("total", 0) or 0)
        tx_item["nft_total_sales"] = total  # tạm dùng như proxy thô
        tx_item["nft_num_owners"] = max(1, min(total, 10_000))  # tránh 0
        # Floor/avg/market_cap/volume chưa có API public ổn định → giữ 0
    except Exception:
        # bỏ qua, dùng default 0
        pass

async def detect_account_or_tx(
    account_address: str,
    tx_hash: Optional[str] = None,
    explain: bool = False,
    explain_with_llm: bool = False,
) -> Dict[str, Any]:
    """
    Orchestrator chính:
    1) Lấy dữ liệu tx từ Etherscan (nếu có tx_hash), nếu không sẽ build 1 item trống tối thiểu.
    2) Enrich NFT metrics (Rarible).
    3) Gọi model /predict với payload đúng format.
    4) Trả kết quả model + raw inputs (để debug phía FE nếu cần).
    """
    if not account_address:
        return {"error": "account_address is required"}

    if tx_hash:
        tx_item = await _build_tx_item_from_hash(tx_hash)
    else:
        # nếu không có tx_hash, tạo item “no-tx” tối thiểu vẫn hợp lệ với model
        tx_item = {
            "from_address": account_address,
            "to_address": "",
            "value": 0, "gasPrice": 0, "gasUsed": 0, "timestamp": 0,
            "function_call": [],
            "token_value": 0, "nft_floor_price": 0, "nft_average_price": 0,
            "nft_total_volume": 0, "nft_total_sales": 0, "nft_num_owners": 0, "nft_market_cap": 0,
        }

    # enrich NFT metrics nhẹ
    await _enrich_nft_metrics(account_address, tx_item)

    payload = {
        "account_address": account_address,
        "transaction_history": [tx_item],
        "explain": bool(explain),
        "explain_with_llm": bool(explain_with_llm),
    }

    # Gọi model
    model_res = await model_predict(payload)

    return {
        "model_result": model_res,
        "used_payload": payload,   # hữu ích cho debug FE; bỏ nếu không muốn trả
    }
