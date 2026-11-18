
import json
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ingestion.common import (
    ROOT,
    META,
    allowed_url,
    canonical_url,
    get_headers,
    get_timeout,
    delay,
    save_json,
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

PDF_EXTENSIONS = (".pdf",)


def is_relevant_link(url, label):
    target = (url + " " + label).lower()

    return (
        any(hint in target for hint in HINTS)
        or url.lower().split("?")[0].endswith(PDF_EXTENSIONS)
    )


def main():
    config_path = ROOT / "config" / "sources.json"

    config = json.loads(
        config_path.read_text(encoding="utf-8")
    )

    sources = config["primary"]

    found = {}
    errors = []
    rejected_links = []

    session = requests.Session()

    for source in sources:
        url = canonical_url(source["url"])

        try:
            if not allowed_url(url):
                raise ValueError("Seed URL is outside the allowed domain")

            response = session.get(
                url,
                headers=get_headers(),
                timeout=get_timeout(),
                verify=True,
                allow_redirects=True,
            )

            response.raise_for_status()

            if not allowed_url(response.url):
                raise ValueError(
                    f"Redirect outside allowed domain: {response.url}"
                )

            final_url = canonical_url(response.url)

            found[final_url] = {
                "url": final_url,
                "title": source["name"],
                "source_type": source["type"],
                "depth": 0,
                "seed": True,
            }

            soup = BeautifulSoup(response.text, "lxml")

            discovered_count = 0

            for anchor in soup.select("a[href]"):
                raw_url = urljoin(
                    response.url,
                    anchor.get("href", ""),
                )

                # IMPORTANT: Validate before canonicalisation.
                if not allowed_url(raw_url):
                    rejected_links.append({
                        "source": final_url,
                        "url": raw_url,
                        "reason": "Outside approved host or invalid port",
                    })
                    continue

                try:
                    candidate = canonical_url(raw_url)

                    label = " ".join(
                        anchor.get_text(" ", strip=True).split()
                    )

                    if not is_relevant_link(candidate, label):
                        continue

                    if candidate not in found:
                        found[candidate] = {
                            "url": candidate,
                            "title": label[:240] or candidate,
                            "source_type": "discovered_candidate",
                            "depth": 1,
                            "seed": False,
                        }
                        discovered_count += 1

                except (ValueError, TypeError) as exc:
                    rejected_links.append({
                        "source": final_url,
                        "url": raw_url,
                        "reason": str(exc),
                    })
                    continue

            print(
                f"[OK] {source['name']} "
                f"HTTP {response.status_code} "
                f"| {discovered_count} new links"
            )

        except Exception as exc:
            errors.append({
                "url": url,
                "stage": "discovery",
                "error": str(exc),
            })

            print(f"[ERROR] {url}: {exc}")

        finally:
            delay()

    report = {
        "discovered_count": len(found),
        "seed_count": len(sources),
        "successful_seeds": len(sources) - len(errors),
        "sources": list(found.values()),
        "errors": errors,
        "rejected_links_count": len(rejected_links),
        "rejected_links": rejected_links,
        "coverage_warning": (
            "Candidate discovery is not proof of complete scheme coverage."
        ),
    }

    save_json(
        META / "discovery_report.json",
        report,
    )

    print("\nDiscovery completed.")
    print("Successful seeds:", report["successful_seeds"])
    print("Discovered URLs:", report["discovered_count"])
    print("Rejected links:", report["rejected_links_count"])
    print("Errors:", len(errors))
    print("Report: data/metadata/discovery_report.json")


if __name__ == "__main__":
    main()
