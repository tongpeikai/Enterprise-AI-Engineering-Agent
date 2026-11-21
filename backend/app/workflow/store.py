from __future__ import annotations

# ruff: noqa: E501
import sqlite3
from pathlib import Path
from uuid import uuid4

WORKFLOW_STATES = {"queued", "running", "paused", "succeeded", "failed", "cancelled"}
STEP_STATES = WORKFLOW_STATES
TRANSITIONS = {
    "queued": {"running", "cancelled"},
    "running": {"paused", "succeeded", "failed", "cancelled"},
    "paused": {"running", "cancelled"},
    "failed": {"queued"},
    "succeeded": set(),
    "cancelled": set(),
}


class WorkflowStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS workflows (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, name TEXT NOT NULL, status TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS workflow_steps (id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, name TEXT NOT NULL, depends_on TEXT NOT NULL, status TEXT NOT NULL, approval_required INTEGER NOT NULL, retries INTEGER NOT NULL DEFAULT 0, max_retries INTEGER NOT NULL DEFAULT 0, conversation_id TEXT)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS workflow_history (id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, step_id TEXT, from_status TEXT, to_status TEXT NOT NULL, actor TEXT NOT NULL, created_at REAL NOT NULL DEFAULT (unixepoch()))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS workflow_approvals (id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, step_id TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL, created_at REAL NOT NULL DEFAULT (unixepoch()))"
            )

    @staticmethod
    def _validate_dag(steps: list[dict[str, object]]) -> None:
        names = {str(step["name"]) for step in steps}
        graph = {str(step["name"]): set(step.get("depends_on", [])) for step in steps}
        if any(dep not in names for deps in graph.values() for dep in deps):
            raise ValueError("unknown workflow dependency")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                raise ValueError("workflow contains a cycle")
            if name in visited:
                return
            visiting.add(name)
            for dependency in graph[name]:
                visit(dependency)
            visiting.remove(name)
            visited.add(name)

        for name in graph:
            visit(name)

    def create(self, tenant_id: str, name: str, steps: list[dict[str, object]]) -> str:
        self._validate_dag(steps)
        workflow_id = str(uuid4())
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO workflows VALUES (?, ?, ?, 'queued')",
                (workflow_id, tenant_id, name),
            )
            for step in steps:
                db.execute(
                    "INSERT INTO workflow_steps (id, workflow_id, name, depends_on, status, approval_required, max_retries, conversation_id) VALUES (?, ?, ?, ?, 'queued', ?, ?, '')",
                    (
                        str(uuid4()),
                        workflow_id,
                        step["name"],
                        ",".join(step.get("depends_on", [])),
                        int(step.get("approval_required", False)),
                        int(step.get("max_retries", 0)),
                    ),
                )
        return workflow_id

    def get(self, tenant_id: str, workflow_id: str) -> dict[str, object]:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT id, tenant_id, name, status FROM workflows WHERE id=? AND tenant_id=?",
                (workflow_id, tenant_id),
            ).fetchone()
            if row is None:
                raise KeyError("workflow not found")
            steps = db.execute(
                "SELECT id, name, depends_on, status, approval_required, retries, max_retries, conversation_id FROM workflow_steps WHERE workflow_id=?",
                (workflow_id,),
            ).fetchall()
        return {
            "id": row[0],
            "tenant_id": row[1],
            "name": row[2],
            "status": row[3],
            "steps": [
                {
                    "id": s[0],
                    "name": s[1],
                    "depends_on": s[2].split(",") if s[2] else [],
                    "status": s[3],
                    "approval_required": bool(s[4]),
                    "retries": s[5],
                    "max_retries": s[6],
                    "conversation_id": s[7],
                }
                for s in steps
            ],
        }

    def list(self, tenant_id: str) -> list[dict[str, object]]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, tenant_id, name, status FROM workflows "
                "WHERE tenant_id=? ORDER BY rowid DESC",
                (tenant_id,),
            ).fetchall()
        return [
            {"id": row[0], "tenant_id": row[1], "name": row[2], "status": row[3]}
            for row in rows
        ]

    def ready_steps(self, tenant_id: str, workflow_id: str) -> list[dict[str, object]]:
        workflow = self.get(tenant_id, workflow_id)
        done = {
            step["name"] for step in workflow["steps"] if step["status"] == "succeeded"
        }
        return [
            step
            for step in workflow["steps"]
            if step["status"] == "queued"
            and all(dep in done for dep in step["depends_on"])
        ]

    def transition(
        self,
        tenant_id: str,
        workflow_id: str,
        status: str,
        actor: str,
        step_id: str | None = None,
    ) -> None:
        if status not in WORKFLOW_STATES:
            raise ValueError("unknown workflow state")
        with sqlite3.connect(self.path) as db:
            table = "workflow_steps" if step_id else "workflows"
            key = step_id or workflow_id
            row = db.execute(
                f"SELECT status FROM {table} WHERE id=?"
                + (" AND workflow_id=?" if step_id else " AND tenant_id=?"),
                (key, workflow_id if step_id else tenant_id),
            ).fetchone()
            if row is None:
                raise KeyError("workflow item not found")
            if status not in TRANSITIONS[row[0]]:
                raise ValueError(f"invalid transition: {row[0]} -> {status}")
            db.execute(f"UPDATE {table} SET status=? WHERE id=?", (status, key))
            db.execute(
                "INSERT INTO workflow_history (id, workflow_id, step_id, from_status, to_status, actor) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid4()), workflow_id, step_id, row[0], status, actor),
            )

    def approve(
        self, tenant_id: str, workflow_id: str, step_id: str, actor: str, decision: str
    ) -> None:
        if decision not in {"approved", "rejected", "revoked"}:
            raise ValueError("invalid approval decision")
        self.get(tenant_id, workflow_id)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO workflow_approvals (id, workflow_id, step_id, actor, decision) VALUES (?, ?, ?, ?, ?)",
                (str(uuid4()), workflow_id, step_id, actor, decision),
            )
            if decision == "approved":
                db.execute(
                    "UPDATE workflow_steps SET approval_required=0 WHERE id=? AND workflow_id=?",
                    (step_id, workflow_id),
                )

    def attach_conversation(
        self, tenant_id: str, workflow_id: str, step_id: str, conversation_id: str
    ) -> None:
        self.get(tenant_id, workflow_id)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE workflow_steps SET conversation_id=? "
                "WHERE id=? AND workflow_id=?",
                (conversation_id, step_id, workflow_id),
            )

    def increment_retry(self, tenant_id: str, workflow_id: str, step_id: str) -> None:
        self.get(tenant_id, workflow_id)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "UPDATE workflow_steps SET retries=retries+1 "
                "WHERE id=? AND workflow_id=?",
                (step_id, workflow_id),
            )

    def recover_running(self, tenant_id: str, workflow_id: str) -> int:
        state = self.get(tenant_id, workflow_id)
        recovered = 0
        with sqlite3.connect(self.path) as db:
            for step in state["steps"]:
                if step["status"] == "running":
                    db.execute(
                        "UPDATE workflow_steps SET status='queued' WHERE id=?",
                        (step["id"],),
                    )
                    recovered += 1
        return recovered

    def history(self, tenant_id: str, workflow_id: str) -> list[dict[str, object]]:
        self.get(tenant_id, workflow_id)
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT step_id, from_status, to_status, actor, created_at FROM workflow_history WHERE workflow_id=? ORDER BY created_at, id",
                (workflow_id,),
            ).fetchall()
        return [
            {
                "step_id": r[0],
                "from": r[1],
                "to": r[2],
                "actor": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]
