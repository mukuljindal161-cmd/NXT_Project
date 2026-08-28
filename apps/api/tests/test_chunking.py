import pytest
from app.services.ingestion.parsers import ParsedDocument, ParsedPage
from app.services.ingestion.chunker import StructureAwareChunker


def test_structure_aware_chunking():
    chunker = StructureAwareChunker(chunk_size=100, chunk_overlap=20)
    parsed_doc = ParsedDocument(
        pages=[
            ParsedPage(
                page_number=1,
                text="Introduction to the college guidelines. This section explains the basic rules and campus protocols."
            ),
            ParsedPage(
                page_number=2,
                text="Library regulations are strictly enforced. All students must present their IDs at the entrance."
            )
        ],
        full_text="",
        page_count=2
    )

    chunks = chunker.chunk_document(parsed_doc)
    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert chunks[-1].page_number == 2
    assert all(c.token_count > 0 for c in chunks)
