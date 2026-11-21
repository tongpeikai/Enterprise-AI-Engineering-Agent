from backend.app.rag.service import KnowledgeStore, chunk_text


def test_chunking_and_tenant_filtered_citations(tmp_path) -> None:
    assert len(chunk_text("one two three four", size=3, overlap=1)) == 2
    store = KnowledgeStore(tmp_path / "knowledge.sqlite")
    store.ingest("org-a", "handbook.md", "deployment uses docker and postgres")
    store.ingest("org-b", "private.md", "deployment uses another system")
    results = store.search("org-a", "docker")
    assert len(results) == 1
    assert results[0].source == "handbook.md"
    assert store.search("org-b", "docker") == []
