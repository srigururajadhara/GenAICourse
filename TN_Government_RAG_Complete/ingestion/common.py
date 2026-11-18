import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import certifi
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

ROOT = Path(__file__).resolve().parents[1]
RAW_HTML = ROOT / "data" / "raw" / "html"
RAW_PDF = ROOT / "data" / "raw" / "pdfs"
META = ROOT / "data" / "metadata"
for directory in (RAW_HTML, RAW_PDF, META):
    directory.mkdir(parents=True, exist_ok=True)

DEFAULT_HOSTS = {"tn.gov.in", "www.tn.gov.in"}


def allowed_hosts():
    # Config is deliberately simple; runtime default remains the official portal.
    return set(DEFAULT_HOSTS)


def canonical_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL cannot be empty")
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"Invalid URL: {url}")
    if parsed.port and parsed.port not in (80, 443):
        raise ValueError("Non-standard URL ports are not allowed")
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    # Keep query string exactly as supplied; query-driven PHP pages depend on it.
    return urlunparse((scheme, host, path, "", parsed.query, ""))


def allowed_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return (
            p.scheme.lower() in ("http", "https")
            and (p.hostname or "").lower() in allowed_hosts()
            and not p.username and not p.password
            and (p.port is None or p.port in (80, 443))
        )
    except (TypeError, ValueError):
        return False


def url_id(url: str) -> str:
    return hashlib.sha256(canonical_url(url).encode("utf-8")).hexdigest()[:24]


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def get_headers():
    return {
        "User-Agent": os.getenv(
            "USER_AGENT",
            "TN-Schemes-ResearchBot/1.0 (+educational research)"
        ),
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    }


def get_timeout():
    return max(5, int(os.getenv("REQUEST_TIMEOUT", "30")))


def delay():
    time.sleep(max(1.0, float(os.getenv("CRAWL_DELAY_SECONDS", "2.0"))))
