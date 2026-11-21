from backend.app.workflow.store import WorkflowStore


def test_workflow_dependencies_and_tenant_acl(tmp_path) -> None:
    store = WorkflowStore(tmp_path / "workflow.sqlite")
    workflow = store.create(
        "org-a",
        "release",
        [
            {"name": "build"},
            {"name": "deploy", "depends_on": ["build"], "approval_required": True},
        ],
    )
    ready = store.ready_steps("org-a", workflow)
    assert [step["name"] for step in ready] == ["build"]
    try:
        store.ready_steps("org-b", workflow)
    except KeyError:
        pass
    else:
        raise AssertionError("cross-tenant workflow access must fail")
