import pytest
from app.ai.providers.mock import MockAIProvider
from app.services.rag.orchestrator import QueryRouter, QueryIntent, EvidenceValidator
from app.services.retrieval.retriever import RetrievedChunk
from uuid import uuid4


def test_query_router_classification():
    router = QueryRouter()
    assert router.classify("Hello there") == QueryIntent.GENERAL_CONVERSATION
    assert router.classify("When is the semester fee due?") == QueryIntent.COLLEGE_KNOWLEDGE
    assert router.classify("Give me a recipe for chocolate cake") == QueryIntent.UNSUPPORTED


def test_evidence_validator():
    # Test valid chunk
    valid_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        document_title="Fee Policy",
        content="The semester fee must be paid before the deadline of September 15.",
        similarity_score=0.85,
        token_count=15
    )
    assert EvidenceValidator.validate([valid_chunk], threshold=0.65) is True

    # Test below threshold
    low_sim_chunk = RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        document_title="Irrelevant Doc",
        content="Some miscellaneous text that has nothing to do with the prompt.",
        similarity_score=0.45,
        token_count=15
    )
    assert EvidenceValidator.validate([low_sim_chunk], threshold=0.65) is False
    assert EvidenceValidator.validate([]) is False


def test_mock_ai_provider_embedding():
    provider = MockAIProvider(dimensions=768)
    vec1 = provider.embed("Library hours and book return policies")
    vec2 = provider.embed("Library hours and book return policies")
    assert len(vec1) == 768
    assert vec1 == vec2  # Deterministic
