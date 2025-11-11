import re

def is_evm_address(addr: str) -> bool:
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", addr or ""))


def hex_selector(data: str | None) -> str:
    if not data: return ""
    d = data.lower()
    if d.startswith("0x"): d = d[2:]
    return "0x" + d[:8] if len(d) >= 8 else ""