# RAG Design

KnowledgeStore keeps tenant-scoped document metadata and FTS5 chunks in SQLite. Ingestion computes SHA-256 for duplicate detection, increments source versions, supports configurable overlap, and records PDF page numbers. Search always binds `tenant_id`, applies top-k/threshold and text deduplication, and returns document/chunk/source/page citations. Deletion removes both document metadata and chunks. The answer endpoint separates evidence context and citations from generated text; no evidence produces an explicit no-results answer.
