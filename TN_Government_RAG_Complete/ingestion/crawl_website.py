
import json
import os
import re
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from ingestion.common import (
    ROOT,
    RAW_HTML,
    RAW_PDF,
    META,
    allowed_url,
    canonical_url,
    url_id,
    save_json,
    get_headers,
    get_timeout,
    delay,
)


HINTS = (
    "scheme",
    "schemes",
    "beneficiar",
    "department",
    "welfare",
    "social",
    "education",
    "scholarship",
    "pension",
    "women",
    "student",
    "agriculture",
    "health",
    "disability",
)

PDF_RE = re.compile(r"\.pdf(?:$|[?#])", re.I)


def robots_check(url, session, cache):
    """
    Check whether the website allows crawling the requested URL.
    Robots.txt results are cached per domain.
    """

    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    if origin not in cache:
        parser = RobotFileParser()
        robots_url = origin + "/robots.txt"

        try:
            response = session.get(
                robots_url,
                headers=get_headers(),
                timeout=get_timeout(),
            )

            if response.status_code == 404:
                parser.parse([
                    "User-agent: *",
                    "Allow: /",
                ])
            else:
                response.raise_for_status()
                parser.parse(response.text.splitlines())

            cache[origin] = parser

        except requests.RequestException as exc:
            cache[origin] = exc

    entry = cache[origin]

    if isinstance(entry, Exception):
        return False, f"robots.txt could not be checked: {entry}"

    agent = os.getenv("ROBOTS_USER_AGENT", "*")

    return entry.can_fetch(agent, url), "robots.txt"


def extract_html_content(html: str, base_url: str):
    """
    Extract useful text and relevant links from Tamil Nadu
    Government scheme pages and other government portal pages.

    Important:
    Tamil Nadu scheme detail pages use the CSS structure:

        .scheme_det
            table.ng-table

    The actual scheme information is inside this table.
    """

    soup = BeautifulSoup(html, "lxml")

    # Get the original browser page title.
    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title
        else ""
    )

    # Remove scripts and elements that do not contain
    # useful main-page content.
    for element in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "nav",
        "footer",
        "header",
    ]):
        element.decompose()

    # --------------------------------------------------
    # 1. Tamil Nadu Government scheme detail extraction
    # --------------------------------------------------

    scheme_container = soup.select_one(".scheme_det")

    if scheme_container:

        # The actual scheme information is inside ng-table.
        main_element = (
            scheme_container.select_one("table.ng-table")
            or scheme_container.find("table")
            or scheme_container
        )

        # Extract the actual scheme title from the table.
        for row in main_element.select("tr"):

            cells = row.find_all(
                ["td", "th"],
                recursive=False,
            )

            if len(cells) >= 2:

                label = cells[0].get_text(
                    " ",
                    strip=True,
                ).lower()

                if (
                    "scheme title" in label
                    or "scheme name" in label
                ):

                    extracted_title = cells[-1].get_text(
                        " ",
                        strip=True,
                    )

                    if extracted_title:
                        title = extracted_title

                    break

    # --------------------------------------------------
    # 2. Generic government page extraction fallback
    # --------------------------------------------------

    else:

        main_element = (
            soup.select_one(".innerpage-content")
            or soup.select_one(".custom-innersection")
            or soup.find("main")
            or soup.find(
                id=re.compile(r"content|main", re.I)
            )
            or soup.body
            or soup
        )

    # --------------------------------------------------
    # 3. Extract visible text
    # --------------------------------------------------

    text = "\n".join(
        line.strip()
        for line in main_element.stripped_strings
        if line.strip()
    )

    # --------------------------------------------------
    # 4. Discover relevant links
    # --------------------------------------------------

    links = []

    for anchor in soup.select("a[href]"):

        raw_url = urljoin(
            base_url,
            anchor.get("href", ""),
        )

        # Validate before canonicalizing.
        if not allowed_url(raw_url):
            continue

        try:
            candidate = canonical_url(raw_url)

        except (ValueError, TypeError):
            continue

        label = anchor.get_text(
            " ",
            strip=True,
        ).lower()

        target = (
            candidate + " " + label
        ).lower()

        relevant = (
            any(hint in target for hint in HINTS)
            or bool(PDF_RE.search(candidate))
        )

        if relevant:
            links.append(candidate)

    return title, text, sorted(set(links))


def main():

    # --------------------------------------------------
    # 1. Load configured seed URLs
    # --------------------------------------------------

    config_path = ROOT / "config" / "sources.json"

    config = json.loads(
        config_path.read_text(encoding="utf-8")
    )

    seed_urls = [
        item["url"]
        for item in config.get("primary", [])
    ]

    # Add URLs discovered by discover_sources.py.
    discovery_path = META / "discovery_report.json"

    if discovery_path.exists():

        discovered = json.loads(
            discovery_path.read_text(encoding="utf-8")
        )

        seed_urls.extend(
            item["url"]
            for item in discovered.get("sources", [])
            if item.get("url")
        )

    # Remove duplicate URLs.
    unique_urls = dict.fromkeys(seed_urls)

    queue = deque(
        (canonical_url(url), 0)
        for url in unique_urls
    )

    # --------------------------------------------------
    # 2. Crawl configuration
    # --------------------------------------------------

    max_pages = max(
        1,
        int(os.getenv("MAX_PAGES", "250")),
    )

    max_depth = max(
        0,
        int(os.getenv("MAX_DEPTH", "3")),
    )

    max_pdf_bytes = (
        max(1, int(os.getenv("MAX_PDF_MB", "40")))
        * 1024
        * 1024
    )

    # --------------------------------------------------
    # 3. Initialize crawler
    # --------------------------------------------------

    session = requests.Session()

    robots_cache = {}

    seen = set()

    html_records = []
    pdf_records = []
    failures = []
    blocked = []

    print("\nStarting Tamil Nadu Government crawler...")
    print("Maximum pages:", max_pages)
    print("Maximum depth:", max_depth)
    print("Initial URLs:", len(queue))

    # --------------------------------------------------
    # 4. Main crawling loop
    # --------------------------------------------------

    while queue and len(seen) < max_pages:

        url, depth = queue.popleft()

        if url in seen or not allowed_url(url):
            continue

        seen.add(url)

        # Check robots.txt.
        permitted, robots_source = robots_check(
            url,
            session,
            robots_cache,
        )

        if not permitted:

            blocked.append({
                "url": url,
                "reason": robots_source,
            })

            print("[ROBOTS BLOCKED]", url)

            continue

        try:

            response = session.get(
                url,
                headers=get_headers(),
                timeout=get_timeout(),
                verify=True,
                allow_redirects=True,
                stream=True,
            )

            response.raise_for_status()

            final_url = canonical_url(response.url)

            # Prevent redirects outside the allowed domain.
            if not allowed_url(final_url):

                failures.append({
                    "url": url,
                    "error": (
                        "Redirect outside allowlist: "
                        + final_url
                    ),
                })

                continue

            content_type = response.headers.get(
                "Content-Type",
                "",
            ).lower()

            # --------------------------------------------------
            # 5. PDF processing
            # --------------------------------------------------

            is_pdf = (
                "application/pdf" in content_type
                or bool(PDF_RE.search(final_url))
            )

            if is_pdf:

                length = response.headers.get(
                    "Content-Length"
                )

                if length and int(length) > max_pdf_bytes:

                    raise ValueError(
                        "PDF exceeds MAX_PDF_MB limit "
                        f"({length} bytes)"
                    )

                chunks = []
                total = 0

                for chunk in response.iter_content(
                    chunk_size=1024 * 128
                ):

                    if not chunk:
                        continue

                    total += len(chunk)

                    if total > max_pdf_bytes:

                        raise ValueError(
                            "PDF exceeded MAX_PDF_MB "
                            "while downloading"
                        )

                    chunks.append(chunk)

                payload = b"".join(chunks)

                # Verify actual PDF file signature.
                if not payload.startswith(b"%PDF"):

                    raise ValueError(
                        "Response declared as PDF "
                        "but did not contain a PDF signature"
                    )

                path = (
                    RAW_PDF
                    / f"{url_id(final_url)}.pdf"
                )

                path.write_bytes(payload)

                pdf_records.append({
                    "url": final_url,
                    "path": str(path.relative_to(ROOT)),
                    "bytes": len(payload),
                    "status": "downloaded",
                    "depth": depth,
                })

                print("[PDF]", final_url)

            # --------------------------------------------------
            # 6. HTML processing
            # --------------------------------------------------

            elif (
                "html" in content_type
                or "xhtml" in content_type
                or not content_type
            ):

                body = response.content

                if len(body) > 12 * 1024 * 1024:

                    raise ValueError(
                        "HTML page exceeded 12 MB limit"
                    )

                encoding = response.encoding or "utf-8"

                html = body.decode(
                    encoding,
                    errors="replace",
                )

                title, text, candidates = extract_html_content(
                    html,
                    final_url,
                )

                # --------------------------------------------------
                # 7. Validate extracted content
                # --------------------------------------------------

                if text.strip():

                    record = {
                        "url": final_url,
                        "title": title,
                        "text": text,
                        "depth": depth,
                        "status_code": response.status_code,
                        "content_type": content_type,
                    }

                    path = (
                        RAW_HTML
                        / f"{url_id(final_url)}.json"
                    )

                    save_json(path, record)

                    html_records.append({
                        "url": final_url,
                        "title": title,
                        "path": str(path.relative_to(ROOT)),
                        "depth": depth,
                        "status": "extracted",
                        "text_length": len(text),
                    })

                else:

                    failures.append({
                        "url": final_url,
                        "error": "No visible text extracted",
                    })

                # Add discovered links to the queue.
                if depth < max_depth:

                    for candidate in candidates:

                        if candidate not in seen:
                            queue.append(
                                (candidate, depth + 1)
                            )

                print(
                    f"[HTML] {title[:70]} "
                    f"({len(text)} chars)"
                )

            # --------------------------------------------------
            # 8. Unsupported content types
            # --------------------------------------------------

            else:

                failures.append({
                    "url": final_url,
                    "error": (
                        "Unsupported content type: "
                        + content_type
                    ),
                })

        except Exception as exc:

            failures.append({
                "url": url,
                "error": str(exc),
            })

            print("[FAILED]", url, exc)

        finally:

            response.close() if "response" in locals() else None

            delay()

    # --------------------------------------------------
    # 9. Generate crawl report
    # --------------------------------------------------

    report = {

        "attempted_unique_urls": len(seen),

        "html_extracted": len(html_records),

        "pdf_downloaded": len(pdf_records),

        "failed": len(failures),

        "robots_blocked": len(blocked),

        "html_records": html_records,

        "pdf_records": pdf_records,

        "failures": failures,

        "robots_blocked_urls": blocked,

        "max_pages": max_pages,

        "max_depth": max_depth,

        "coverage_warning": (
            "Bounded same-domain crawl only. "
            "It does not establish complete coverage "
            "of all Tamil Nadu Government schemes "
            "or external department websites."
        ),
    }

    save_json(
        META / "crawl_report.json",
        report,
    )

    print("\n===================================")
    print("CRAWL COMPLETED")
    print("===================================")

    print(
        "Crawl report saved:",
        META / "crawl_report.json",
    )

    print("\nSummary:")

    print({
        key: report[key]
        for key in (
            "attempted_unique_urls",
            "html_extracted",
            "pdf_downloaded",
            "failed",
            "robots_blocked",
        )
    })


if __name__ == "__main__":
    main()
