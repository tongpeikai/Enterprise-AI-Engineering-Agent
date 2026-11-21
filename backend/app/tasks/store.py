import sqlite3
from pathlib import Path
from uuid import uuid4

VALID_TRANSITIONS = {
    "queued": {"running", "cancelled"},
    "running": {"paused", "succeeded", "failed", "cancelled"},
    "paused": {"running", "cancelled"},
    "failed": {"queued"},
    "succeeded": set(),
    "cancelled": set(),
}


class TaskStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS tasks "
                "(id TEXT PRIMARY KEY, org_id TEXT NOT NULL, title TEXT NOT NULL, "
                "status TEXT NOT NULL, conversation_id TEXT)"
            )

    def create(self, org_id: str, title: str) -> dict[str, str]:
        task = {
            "id": str(uuid4()),
            "org_id": org_id,
            "title": title,
            "status": "queued",
            "conversation_id": "",
        }
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?)", tuple(task.values()))
        return task

    def list(self, org_id: str) -> list[dict[str, str]]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, org_id, title, status, conversation_id "
                "FROM tasks WHERE org_id=?",
                (org_id,),
            ).fetchall()
        keys = ("id", "org_id", "title", "status", "conversation_id")
        return [dict(zip(keys, row, strict=True)) for row in rows]

    def get(self, task_id: str, org_id: str) -> dict[str, str]:
        rows = [task for task in self.list(org_id) if task["id"] == task_id]
        if not rows:
            raise KeyError("task not found")
        return rows[0]

    def attach_conversation(
        self, task_id: str, org_id: str, conversation_id: str
    ) -> dict[str, str]:
        self.get(task_id, org_id)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE tasks SET conversation_id=?, status='running' "
                "WHERE id=? AND org_id=?",
                (conversation_id, task_id, org_id),
            )
        return self.get(task_id, org_id)

    def transition(self, task_id: str, org_id: str, status: str) -> dict[str, str]:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT id, org_id, title, status, conversation_id "
                "FROM tasks WHERE id=? AND org_id=?",
                (task_id, org_id),
            ).fetchone()
            if row is None:
                raise KeyError("task not found")
            if status not in VALID_TRANSITIONS[row[3]]:
                raise ValueError(f"invalid transition: {row[3]} -> {status}")
            db.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
        return {
            "id": row[0],
            "org_id": row[1],
            "title": row[2],
            "status": status,
            "conversation_id": row[4],
        }
