# ruff: noqa: E501
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from time import time


@dataclass(frozen=True)
class RetrievalCase:
    query: str
    relevant_document_ids: set[str]


def retrieval_scores(
    cases: list[RetrievalCase], results: list[list[str]], k: int
) -> dict[str, float]:
    if not cases or len(cases) != len(results):
        raise ValueError("cases and results must have equal non-zero length")
    hits = [
        set(items[:k]) & case.relevant_document_ids
        for case, items in zip(cases, results, strict=True)
    ]
    recall = sum(bool(hit) for hit in hits) / len(cases)
    precision = sum(len(hit) / max(k, 1) for hit in hits) / len(cases)
    reciprocal = []
    for case, items in zip(cases, results, strict=True):
        reciprocal.append(
            next(
                (
                    1 / (index + 1)
                    for index, item in enumerate(items[:k])
                    if item in case.relevant_document_ids
                ),
                0.0,
            )
        )
    return {
        "recall_at_k": recall,
        "precision_at_k": precision,
        "mrr": sum(reciprocal) / len(reciprocal),
        "hit_rate_at_k": recall,
    }


class BenchmarkStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS benchmark_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL, kind TEXT NOT NULL, mode TEXT NOT NULL, result_json TEXT NOT NULL, created_at REAL NOT NULL)"
            )

    def save(
        self, tenant_id: str, kind: str, mode: str, result: dict[str, float]
    ) -> int:
        with sqlite3.connect(self.path) as db:
            cursor = db.execute(
                "INSERT INTO benchmark_runs (tenant_id, kind, mode, result_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (tenant_id, kind, mode, json.dumps(result), time()),
            )
            return int(cursor.lastrowid)

    def list(self, tenant_id: str) -> list[dict[str, object]]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, kind, mode, result_json, created_at FROM benchmark_runs WHERE tenant_id=? ORDER BY id DESC",
                (tenant_id,),
            ).fetchall()
        return [
            {
                "id": row[0],
                "kind": row[1],
                "mode": row[2],
                "result": json.loads(row[3]),
                "created_at": row[4],
            }
            for row in rows
        ]
