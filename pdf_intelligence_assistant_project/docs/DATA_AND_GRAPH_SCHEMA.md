# Data Model and Knowledge Graph Schema

## 1. Design objectives

- Every index record and graph fact must trace back to an exact uploaded document version and page.
- All queries must enforce workspace/document scope.
- Re-ingestion must be idempotent.
- Entity and relation schemas must be explicit, versioned and validated.

## 2. Core records

### Workspace

- `workspace_id` (stable identifier)
- `owner_user_id`
- `created_at`, `status`, `settings`

### Document

- `document_id`, `workspace_id`
- `display_name`, `original_filename`, `content_sha256`, `mime_type`, `size_bytes`
- `created_at`, `uploaded_by`, `status`, `active_version_id`
- `retention_policy_id` (when configured)

### DocumentVersion

- `document_version_id`, `document_id`, `version_number`
- `source_file_uri` (private storage reference)
- `parser_name`, `parser_version`, `ocr_used`, `extraction_config_version`
- `page_count`, `extraction_quality`, `created_at`

### CanonicalBlock

- `block_id`, `document_version_id`, `page_number`, `block_order`
- `block_type` (heading, paragraph, list, table, caption, other)
- `section_path`, `text`, `source_offsets`, `extraction_method`, `quality_metadata`

### Chunk

- `chunk_id`, `document_version_id`, `workspace_id`, `document_id`
- `page_start`, `page_end`, `section_path`, `text`, `token_count`
- `chunker_version`, `embedding_model`, `content_hash`

### IngestionJob / PipelineRun

- `job_id`, `document_version_id`, `pipeline_name`, `stage_name`, `status`
- `attempt`, `started_at`, `finished_at`, `error_code`, `safe_error_message`
- `config_version`, `correlation_id`

### ChatSession / Message

- `session_id`, `workspace_id`, `user_id`, `document_scope`
- message role, content, timestamp, model/prompt version and citation references
- do not retain unnecessary raw document content in application logs

## 3. Graph schema (proposed initial ontology)

### Nodes

- `Workspace {workspace_id}`
- `Document {document_id, document_version_id, workspace_id, title}`
- `Chunk {chunk_id, page_start, page_end, workspace_id, document_id, document_version_id}`
- `Entity {entity_id, canonical_name, entity_type, aliases, normalized_key}`
- `EntityMention {mention_id, entity_id, chunk_id, page_number, surface_form, start_offset, end_offset, confidence, extraction_run_id}`

### Relationships

- `(Workspace)-[:OWNS]->(Document)`
- `(Document)-[:HAS_VERSION]->(DocumentVersion)` (or document version as an explicit node)
- `(DocumentVersion)-[:HAS_CHUNK]->(Chunk)`
- `(Chunk)-[:HAS_MENTION]->(EntityMention)-[:REFERS_TO]->(Entity)`
- `(Entity)-[:USES|DEPENDS_ON|STORES_DATA_IN|PROVIDES|PROCESSES|PART_OF|CONNECTS_TO]->(Entity)` only when explicitly supported by evidence.

For evidence-bearing entity-to-entity relations, store provenance properties on the relationship or use a `RelationAssertion` node so multiple source pages/chunks can support, contradict or qualify the same assertion. The preferred implementation should use a provenance-friendly `RelationAssertion` node if facts can have multiple sources or confidence values.

### Initial entity types

`PERSON`, `ORGANIZATION`, `TECHNOLOGY`, `SERVICE`, `DATABASE`, `API`, `FEATURE`, `INFRASTRUCTURE_COMPONENT`, `PROTOCOL`, `SECURITY_CONTROL`, `METRIC`, `PLAN`, `OTHER`.

### Initial relation types

`USES`, `DEPENDS_ON`, `STORES_DATA_IN`, `PROVIDES`, `AUTHENTICATES`, `PROCESSES`, `CONNECTS_TO`, `PART_OF`, `MANAGES`, `PUBLISHES_TO`, `CONSUMES_FROM`, `SUPPORTS`.

Only an allowlisted subset should be activated in v1.0 after review. Extraction must not infer a relation from proximity alone.

## 4. Provenance requirement

Every `EntityMention` and `RelationAssertion` must include:
- workspace, document and document version IDs;
- chunk ID and page number(s);
- exact supporting quote/span;
- extractor/model version and run ID;
- confidence or validation state;
- creation time.

A graph search result without retrievable source provenance shall be excluded from answer evidence.

## 5. Index partitioning and isolation

- FAISS index partitions or ID selectors must map to a workspace/document/version manifest.
- BM25 documents must carry identical scope metadata.
- Neo4j nodes and relationships must be filtered by workspace and selected document/version.
- Cache keys must include user/workspace, document scope, document version and retrieval config version.
- Never rely only on opaque filenames or UI state for access control.

## 6. Deletion and rebuild

Rebuild indexes from canonical blocks for the target document version. Deleting a document must remove all of its chunks, vectors, lexical records, graph mentions, graph assertions, summaries, chat citations and cached results according to the configured retention policy. Shared canonical entities may remain only if their provenance and visibility are still correct; avoid globally shared entity nodes that leak relationships across workspaces.

## 7. Schema versioning

Persist `graph_schema_version`, `entity_extractor_version`, `relation_extractor_version`, `chunker_version` and `embedding_model`. Schema migration and re-indexing must be explicit, testable and rollback-aware.
