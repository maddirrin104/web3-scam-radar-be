from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    p = urlparse(url)
    return p.hostname or ""