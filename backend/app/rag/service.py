import hashlib
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from backend.app.tools.security import safe_workspace_path


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    tenant_id: str
    text: str
    source: str
    ordinal: int
    page: int | None = None
    score: float = 0.0


@dataclass(frozen=True)
class Document:
    id: str
    tenant_id: str
    source: str
    sha256: str
    version: int
    status: str


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    if size <= overlap or size < 1:
        raise ValueError("chunk size must exceed overlap")
    words = text.split()
    step = size - overlap
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step)]


def parse_pdf(data: bytes) -> list[tuple[int, str]]:
    """Extract basic page text from a PDF without executing embedded content."""
    pages = data.split(b"/Type /Page")
    result = []
    for number, page in enumerate(pages[1:], 1):
        text = b" ".join(re.findall(rb"\(([^()]*)\)", page)).decode("utf-8", "ignore")
        if text.strip():
            result.append((number, text))
    if not result:
        raise ValueError("PDF text extraction failed")
    return result


class KnowledgeStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS documents ("
                "id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, source TEXT NOT NULL, "
                "sha256 TEXT NOT NULL, version INTEGER NOT NULL, status TEXT NOT NULL, "
                "UNIQUE(tenant_id, source, version))"
            )
            db.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5("
                "id UNINDEXED, document_id UNINDEXED, tenant_id UNINDEXED, text, "
                "source UNINDEXED, ordinal UNINDEXED, page UNINDEXED)"
            )

    def ingest(
        self,
        tenant_id: str,
        source: str,
        text: str,
        *,
        size: int = 800,
        overlap: int = 100,
        pages: list[tuple[int, str]] | None = None,
    ) -> str:
        content = text.encode()
        digest = hashlib.sha256(content).hexdigest()
        with sqlite3.connect(self.path) as db:
            existing = db.execute(
                "SELECT id FROM documents WHERE tenant_id=? AND sha256=? "
                "AND status='ready'",
                (tenant_id, digest),
            ).fetchone()
            if existing:
                return existing[0]
            version = (
                db.execute(
                    "SELECT COALESCE(MAX(version), 0) FROM documents "
                    "WHERE tenant_id=? AND source=?",
                    (tenant_id, source),
                ).fetchone()[0]
                or 0
            ) + 1
            document_id = str(uuid4())
            db.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, 'ready')",
                (document_id, tenant_id, source, digest, version),
            )
            parts = pages or [(None, text)]
            ordinal = 0
            for page, page_text in parts:
                for value in chunk_text(page_text, size, overlap):
                    db.execute(
                        "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            str(uuid4()),
                            document_id,
                            tenant_id,
                            value,
                            source,
                            ordinal,
                            page,
                        ),
                    )
                    ordinal += 1
        return document_id

    def ingest_bytes(
        self,
        tenant_id: str,
        source: str,
        data: bytes,
        *,
        size: int = 800,
        overlap: int = 100,
    ) -> str:
        suffix = Path(source).suffix.lower()
        if suffix in {".txt", ".md", ".markdown"}:
            return self.ingest(
                tenant_id, source, data.decode("utf-8"), size=size, overlap=overlap
            )
        if suffix == ".pdf":
            return self.ingest(
                tenant_id,
                source,
                " ".join(text for _, text in parse_pdf(data)),
                size=size,
                overlap=overlap,
                pages=parse_pdf(data),
            )
        raise ValueError("unsupported document type")

    def delete(self, tenant_id: str, document_id: str) -> None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT id FROM documents WHERE id=? AND tenant_id=?",
                (document_id, tenant_id),
            ).fetchone()
            if row is None:
                raise KeyError("document not found")
            db.execute(
                "DELETE FROM chunks WHERE document_id=? AND tenant_id=?",
                (document_id, tenant_id),
            )
            db.execute(
                "DELETE FROM documents WHERE id=? AND tenant_id=?",
                (document_id, tenant_id),
            )

    def list_documents(self, tenant_id: str) -> list[Document]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, tenant_id, source, sha256, version, status "
                "FROM documents WHERE tenant_id=?",
                (tenant_id,),
            ).fetchall()
        return [Document(*row) for row in rows]

    def search(
        self, tenant_id: str, query: str, limit: int = 5, threshold: float = 0.0
    ) -> list[Chunk]:
        if not query.strip() or limit < 1:
            return []
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, document_id, tenant_id, text, source, ordinal, page, "
                "bm25(chunks) FROM chunks WHERE chunks MATCH ? AND tenant_id=? "
                "ORDER BY rank LIMIT ?",
                (query, tenant_id, limit * 3),
            ).fetchall()
        unique: dict[str, Chunk] = {}
        for row in rows:
            score = max(0.0, -float(row[7]))
            item = Chunk(*row[:7], score=score)
            if score >= threshold and item.text not in {
                x.text for x in unique.values()
            }:
                unique[item.text] = item
        return list(unique.values())[:limit]


def load_text_file(workspace: str | Path, relative_path: str) -> tuple[str, str]:
    path = safe_workspace_path(workspace, relative_path)
    if path.suffix.lower() not in {".txt", ".md", ".markdown", ".pdf"}:
        raise ValueError("unsupported document type")
    if path.suffix.lower() == ".pdf":
        return " ".join(text for _, text in parse_pdf(path.read_bytes())), str(path)
    return path.read_text(encoding="utf-8"), str(path)
