import os
import sys
import unittest

# Add apps/api to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/api")))


class TestCollegeRAG(unittest.TestCase):
    def test_password_hashing(self):
        from app.security.passwords import get_password_hash, verify_password
        raw = "StrongPassword123!"
        hashed = get_password_hash(raw)
        self.assertNotEqual(hashed, raw)
        self.assertTrue(verify_password(raw, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_tokens(self):
        from app.security.tokens import create_access_token, decode_access_token
        data = {"sub": "12345-uuid", "email": "test@example.edu", "role": "student"}
        token = create_access_token(data)
        self.assertIsInstance(token, str)
        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "12345-uuid")
        self.assertEqual(payload["email"], "test@example.edu")

    def test_chunking(self):
        from app.services.ingestion.parsers import ParsedDocument, ParsedPage
        from app.services.ingestion.chunker import StructureAwareChunker
        chunker = StructureAwareChunker(chunk_size=100, chunk_overlap=20)
        parsed_doc = ParsedDocument(
            pages=[
                ParsedPage(page_number=1, text="Introduction to the college guidelines. This section explains the basic rules and campus protocols."),
                ParsedPage(page_number=2, text="Library regulations are strictly enforced. All students must present their IDs at the entrance.")
            ],
            full_text="",
            page_count=2
        )
        chunks = chunker.chunk_document(parsed_doc)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0].page_number, 1)

    def test_query_router(self):
        from app.services.rag.orchestrator import QueryRouter, QueryIntent
        router = QueryRouter()
        self.assertEqual(router.classify("Hello there"), QueryIntent.GENERAL_CONVERSATION)
        self.assertEqual(router.classify("When is the semester fee due?"), QueryIntent.COLLEGE_KNOWLEDGE)
        self.assertEqual(router.classify("Give me a recipe for chocolate cake"), QueryIntent.UNSUPPORTED)

    def test_mock_embeddings(self):
        from app.ai.providers.mock import MockAIProvider
        provider = MockAIProvider(dimensions=768)
        vec1 = provider.embed("Hostel rules")
        vec2 = provider.embed("Hostel rules")
        self.assertEqual(len(vec1), 768)
        self.assertEqual(vec1, vec2)


if __name__ == "__main__":
    unittest.main()
