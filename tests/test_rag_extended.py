from backend.app.rag.service import KnowledgeStore, parse_pdf


def test_pdf_pages_versions_duplicates_and_delete(tmp_path) -> None:
    pdf = b"%PDF /Type /Page (first page) /Type /Page (second page)"
    assert parse_pdf(pdf) == [(1, "first page"), (2, "second page")]
    store = KnowledgeStore(tmp_path / "knowledge.sqlite")
    first = store.ingest_bytes("org-a", "guide.pdf", pdf)
    assert store.ingest_bytes("org-a", "guide.pdf", pdf) == first
    assert store.list_documents("org-a")[0].version == 1
    assert store.search("org-a", "first")[0].page == 1
    store.delete("org-a", first)
    assert store.search("org-a", "first") == []
