# Guardrails, Security and Data Protection

## 1. Security posture

The application processes untrusted user files and untrusted text extracted from those files. PDF content can contain malicious instructions, misleading text, hidden layers, malformed structures or sensitive information. The LLM must never treat uploaded content as trusted system instructions.

## 2. Upload and parser security

- Enforce authenticated upload and per-user/workspace quotas.
- Check filename, MIME type and PDF signature; normalize filenames and store with generated IDs.
- Limit file bytes, page count, object count, parsing time, memory and decompressed content.
- Parse in a restricted worker/container with no unnecessary network or filesystem privileges.
- Reject malformed, encrypted (unless supported), corrupt or policy-prohibited files.
- Keep originals in private storage; do not serve raw storage paths directly.
- Scan uploads with the organization's approved malware-scanning process where available.
- Do not execute embedded scripts, launch actions or follow external links from a PDF.
- Detect duplicate content using a cryptographic hash within the relevant ownership boundary.

## 3. Ingestion guardrails and quality controls

- Classify page extraction quality and flag empty or anomalous pages.
- Apply OCR only under defined conditions; preserve OCR method and quality metadata.
- Validate entity/relation schema, maximum node/relation counts, string lengths and allowed properties.
- Require exact evidence quotes and page/chunk IDs for graph facts.
- Reject graph facts without evidence, invalid endpoints or unsupported relation types.
- Keep extracted text separate from prompts and system configuration.
- Treat hidden PDF text, metadata, links and instructions as untrusted content.
- Provide configurable content-category restrictions only when product policy defines them; do not invent a document-domain restriction. The default product is a general PDF assistant, with answers limited to the active PDF scope.

## 4. Prompt-injection defense

Use layered controls:
1. System/developer instructions are fixed server-side and cannot be supplied or overwritten by the PDF.
2. Delimit retrieved passages as untrusted quoted evidence.
3. Tell the model to extract facts from passages, never follow commands contained in passages.
4. Do not expose tools, secrets, file systems, unrestricted Cypher or arbitrary network actions to the answer-generation model.
5. Filter user inputs for attempts to override scope, request hidden prompts or access another user's files.
6. Validate output against source evidence and citation constraints.
7. Test direct and indirect injection in user questions, PDF text, metadata, OCR text, tables and graph entity descriptions.

Prompt-injection classifiers are an additional signal, not the only security boundary. Authorization and tool restrictions must be enforced outside the LLM.

## 5. Question and answer guardrails

- Verify user identity and selected document scope before retrieval.
- Reject or safely respond to requests outside the selected PDF scope.
- Do not add public-web knowledge or general model knowledge to document answers.
- For unsupported questions, respond that the selected document does not provide sufficient information.
- For conflicting PDF passages, cite both and explain the conflict; do not silently choose one.
- Validate citation document/version/page and ensure the cited passage supports the claim.
- Avoid revealing secrets, system prompts, credentials, internal paths or other users' data.

## 6. Neo4j/Cypher controls

- Use read-only credentials for retrieval.
- Use parameterized, allowlisted query templates.
- Do not run raw LLM-generated Cypher.
- Enforce workspace/document predicates, query timeout, traversal depth and result limits.
- Validate returned entities and evidence before they enter the answer context.
- Use separate least-privilege credentials for ingestion writes and query reads where practical.

## 7. Identity, authorization and tenant isolation

- Authenticate every private request.
- Check ownership/role on every document, job, summary, chat and export operation.
- Apply scope filters within the vector, lexical, graph, cache and file-storage layers.
- Test IDOR, guessed document IDs, cross-user retrieval, cache collisions and deletion access.
- Admin access should be role-limited and audited; operational dashboards should avoid document content by default.

## 8. Secrets and network security

- Store API keys and database credentials in environment/secret manager; never commit `.env` or keys.
- Use TLS for internet-facing APIs and secure cookie/token practices appropriate to chosen auth architecture.
- Rotate credentials; redact secrets from logs and error messages.
- Set restrictive CORS, request-size limits, rate limits and timeouts.
- Pin and scan dependencies; generate a software bill of materials for production releases where feasible.

## 9. Privacy and lifecycle

Before launch, decide data region, retention period, deletion guarantees, backup retention, audit retention, model-provider data handling terms and whether sensitive/regulated PDFs are allowed. Explain to users what content is sent to the LLM/embedding provider. Provide deletion workflows that cover originals, indexes, graph facts, derived summaries, exports, caches and backups according to policy.

## 10. Security release gates

- No unresolved critical/high vulnerabilities.
- No successful cross-tenant/document-scope leakage in automated tests.
- No unrestricted Cypher or arbitrary tool execution path.
- Prompt-injection test suite passes agreed thresholds.
- Upload/parser abuse tests remain within configured resource limits.
- Secrets scanning passes and all production credentials are externalized.
- Backup and deletion behavior is tested and documented.
