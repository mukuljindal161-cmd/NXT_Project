import pytest
from app.services.ingestion.parsers import TXTParser, get_document_parser, PDFParser


def test_txt_parser():
    parser = TXTParser()
    content = b"Official Notice: All classes are suspended for the annual college symposium on Friday."
    parsed = parser.parse(content, "notice.txt")
    assert parsed.page_count == 1
    assert "Official Notice" in parsed.full_text


def test_get_document_parser_factory():
    assert isinstance(get_document_parser("doc.pdf"), PDFParser)
    assert isinstance(get_document_parser("notes.txt"), TXTParser)
