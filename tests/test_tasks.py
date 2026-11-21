from backend.app.tasks.store import TaskStore


def test_task_state_machine_and_tenant_filter(tmp_path) -> None:
    store = TaskStore(tmp_path / "tasks.sqlite")
    task = store.create("org-a", "Run tests")
    assert store.list("org-b") == []
    assert store.transition(task["id"], "org-a", "running")["status"] == "running"
    assert store.transition(task["id"], "org-a", "paused")["status"] == "paused"
