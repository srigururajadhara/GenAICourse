from __future__ import annotations

import json
import os
from pathlib import Path

import requests

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8001").rstrip("/")
API_KEY = os.getenv("PDF_ASSISTANT_API_KEY", "local-dev-key-change-before-deployment")
DOCUMENT_ID = os.getenv("EVAL_DOCUMENT_ID", "")
DATASET = Path(__file__).resolve().parents[1] / "evals" / "sample_spotify_questions.jsonl"


def main() -> None:
    if not DOCUMENT_ID:
        raise SystemExit("Set EVAL_DOCUMENT_ID to the uploaded and READY sample PDF document ID")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    cases = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    for case in cases:
        response = requests.post(
            f"{API_BASE}/api/v1/ask", headers=headers, timeout=180,
            json={"document_id": DOCUMENT_ID, "question": case["question"]},
        )
        response.raise_for_status()
        result = response.json()
        citations = result.get("citations", [])
        cited_pages = {item["page"] for item in citations}
        page_hit = not case["answerable"] or bool(cited_pages.intersection(case["expected_pages"]))
        answer = result.get("answer", "").casefold()
        term_hits = sum(term.casefold() in answer for term in case["expected_terms"])
        term_coverage = (term_hits / len(case["expected_terms"])) if case["expected_terms"] else None
        abstention_correct = bool(result.get("abstained")) == (not case["answerable"])
        results.append({
            "id": case["id"], "abstained": result.get("abstained"),
            "expected_answerable": case["answerable"], "citation_page_hit": page_hit,
            "expected_term_coverage": term_coverage, "abstention_correct": abstention_correct,
            "cited_pages": sorted(cited_pages),
        })
        print(json.dumps(results[-1], ensure_ascii=False))
    answerable = [r for r in results if r["expected_answerable"]]
    unanswerable = [r for r in results if not r["expected_answerable"]]
    print("\nSUMMARY")
    print(json.dumps({
        "cases": len(results),
        "answerable_citation_page_hit_rate": sum(r["citation_page_hit"] for r in answerable) / max(1, len(answerable)),
        "unsupported_question_abstention_rate": sum(bool(r["abstained"]) for r in unanswerable) / max(1, len(unanswerable)),
        "answerable_expected_term_coverage_avg": sum(r["expected_term_coverage"] or 0 for r in answerable) / max(1, len(answerable)),
        "abstention_decision_accuracy": sum(r["abstention_correct"] for r in results) / max(1, len(results)),
        "note": "This lightweight smoke evaluation is not a substitute for human faithfulness review or a production release gate.",
    }, indent=2))


if __name__ == "__main__":
    main()
