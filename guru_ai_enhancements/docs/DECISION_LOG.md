# Guru Enhancements — Decision Log

| ID | Date | Decision / observation | Status | Notes |
|---|---|---|---|---|
| DEC-001 | 2026-11-15 | Existing `guru_ai` remains the protected, working baseline; enhancements are isolated in `guru_ai_enhancements`. | Agreed | No source changes to baseline. |
| DEC-002 | 2026-11-15 | Reuse the existing shared `GenAICourse/venv312`; do not create another environment by default. | Agreed | Dependency changes require impact review. |
| DEC-003 | 2026-11-15 | Use the original Field to Future visual direction for Guru. | Visual direction accepted | Detailed UX acceptance criteria still require sign-off. |
| DEC-004 | 2026-11-15 | Open dropdown option text must be readable on a light/high-contrast menu; the screenshot's dark-green-on-near-black state is unacceptable. | Requirement confirmed | Applies to all dropdowns, not only Irrigation. |
| DEC-005 | 2026-11-15 | Advanced RAG Phase 1 is the next technical enhancement track. | Proposed scope | Hybrid retrieval, query rewriting, reranking, evidence gate and evaluation. |
| DEC-006 | 2026-11-15 | Requirements, architecture, RTM and test cases must be prepared and explicitly approved before coding. | Agreed governance | This documentation pack does not authorise implementation. |
| DEC-007 | 2026-11-15 | Screenshot shows upload copy “Limit 200MB per file”, while reviewed API source enforces 30 MB. | Open discrepancy | Verify the currently running backend and make UI copy/API limit consistent before setting the enhanced upload requirement. |

## Open decisions

1. Final evaluation metric thresholds.
2. Starting size and language balance for the human-reviewed evaluation dataset.
3. Cross-encoder model after quality/latency/memory benchmark.
4. Browser and viewport support matrix.
5. Custom dropdown component approach if Streamlit's native dropdown menu cannot be reliably styled.
6. Diagnostic report format and access restrictions.
7. Actual upload size limit in the current working app/backend (screenshot says 200 MB; reviewed API snapshot says 30 MB).
