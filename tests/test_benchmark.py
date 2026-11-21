from backend.app.observability.benchmark import RetrievalCase, retrieval_scores


def test_retrieval_metrics_are_deterministic() -> None:
    scores = retrieval_scores(
        [RetrievalCase("q", {"doc-a"}), RetrievalCase("q2", {"doc-b"})],
        [["doc-a", "doc-x"], ["doc-x", "doc-b"]],
        2,
    )
    assert scores == {
        "recall_at_k": 1.0,
        "precision_at_k": 0.5,
        "mrr": 0.75,
        "hit_rate_at_k": 1.0,
    }
