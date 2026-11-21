import sqlite3
from pathlib import Path
from threading import Lock
from uuid import UUID

from .models import RuntimeHandle


class RunStore:
    """Small durable store for gateway correlation state."""

    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        self._lock = Lock()
        with sqlite3.connect(self._path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS agent_runs "
                "(run_id TEXT PRIMARY KEY, openhands_id TEXT NOT NULL, "
                "status TEXT NOT NULL, "
                "attempt INTEGER NOT NULL DEFAULT 1, cursor TEXT)"
            )

    def save(self, handle: RuntimeHandle, attempt: int = 1) -> None:
        with self._lock, sqlite3.connect(self._path) as db:
            db.execute(
                "INSERT OR REPLACE INTO agent_runs "
                "(run_id, openhands_id, status, attempt, cursor) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    str(handle.run_id),
                    str(handle.openhands_id),
                    handle.status,
                    attempt,
                    None,
                ),
            )

    def get(self, run_id: UUID) -> dict[str, object] | None:
        with self._lock, sqlite3.connect(self._path) as db:
            row = db.execute(
                "SELECT run_id, openhands_id, status, attempt, cursor "
                "FROM agent_runs WHERE run_id=?",
                (str(run_id),),
            ).fetchone()
        if row is None:
            return None
        return {
            "run_id": row[0],
            "openhands_id": row[1],
            "status": row[2],
            "attempt": row[3],
            "cursor": row[4],
        }

    def update_cursor(self, run_id: UUID, cursor: str) -> None:
        with self._lock, sqlite3.connect(self._path) as db:
            db.execute(
                "UPDATE agent_runs SET cursor=? WHERE run_id=?", (cursor, str(run_id))
            )
