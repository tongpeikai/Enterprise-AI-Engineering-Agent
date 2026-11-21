from backend.app.observability.metrics import Metrics


def test_metrics_snapshot_is_observable() -> None:
    metrics = Metrics()
    metrics.increment("task.success")
    with metrics.timer("task.latency"):
        pass
    snapshot = metrics.snapshot()
    assert snapshot.counters == {"task.success": 1}
    assert len(snapshot.durations["task.latency"]) == 1
