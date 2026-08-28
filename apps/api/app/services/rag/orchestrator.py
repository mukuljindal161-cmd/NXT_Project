import os
import json
from enum import Enum
from typing import List, Optional, Generator, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Message, Citation, DocumentChunk, MessageStatus, MessageRole
from app.services.retrieval.retriever import Retriever, RetrievedChunk
from app.ai.providers import get_ai_provider
from app.config import settings


class QueryIntent(str, Enum):
    COLLEGE_KNOWLEDGE = "COLLEGE_KNOWLEDGE"
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    UNSUPPORTED = "UNSUPPORTED"


class QueryRouter:
    def __init__(self):
        self.ai_provider = get_ai_provider()
        prompt_path = os.path.join(os.path.dirname(__file__), "../../ai/prompts/query_router.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.template = f.read()
        except Exception:
            self.template = "Classify question: {question}"

    def classify(self, question: str) -> QueryIntent:
        q_lower = question.strip().lower()

        # Fast heuristic checks for common conversational queries
        greetings = {"hi", "hello", "hey", "good morning", "good evening", "how are you", "who are you", "what can you do", "help"}
        if q_lower in greetings or any(q_lower.startswith(g) for g in ["hi ", "hello ", "hey ", "good morning", "good evening"]) or len(q_lower) < 4:
            return QueryIntent.GENERAL_CONVERSATION

        # Out of bounds / unsupported heuristics
        unsupported_keywords = ["recipe", "bake a cake", "movie trivia", "write a poem", "python script to hack"]
        if any(kw in q_lower for kw in unsupported_keywords):
            return QueryIntent.UNSUPPORTED

        # Default to college knowledge for RAG retrieval
        return QueryIntent.COLLEGE_KNOWLEDGE


class EvidenceValidator:
    @staticmethod
    def validate(retrieved_chunks: List[RetrievedChunk], threshold: Optional[float] = None) -> bool:
        th = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD
        if not retrieved_chunks:
            return False
        # Ensure at least one chunk meets the threshold and has content
        valid_chunks = [c for c in retrieved_chunks if c.similarity_score >= th and len(c.content.strip()) > 20]
        return len(valid_chunks) > 0


class PromptBuilder:
    def __init__(self):
        prompts_dir = os.path.join(os.path.dirname(__file__), "../../ai/prompts")
        try:
            with open(os.path.join(prompts_dir, "system.txt"), "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except Exception:
            self.system_prompt = "You are a College Information Assistant."

        try:
            with open(os.path.join(prompts_dir, "rag_answer.txt"), "r", encoding="utf-8") as f:
                self.rag_template = f.read()
        except Exception:
            self.rag_template = "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion:\n{question}"

    def build_context_string(self, chunks: List[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant college documents found."

        context_parts = []
        for i, chunk in enumerate(chunks):
            page_info = f" (Page {chunk.page_number})" if chunk.page_number else ""
            section_info = f" [{chunk.section_title}]" if chunk.section_title else ""
            context_parts.append(
                f"[Source {i+1}: {chunk.document_title}{page_info}{section_info}]\n{chunk.content}"
            )
        return "\n\n---\n\n".join(context_parts)

    def build_history_string(self, history: List[Message]) -> str:
        if not history:
            return "No previous messages."
        lines = []
        # Include last 4 turns max to stay within context limits
        for msg in history[-4:]:
            role_label = "Student" if msg.role == MessageRole.USER else "Assistant"
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)

    def build_prompt(self, question: str, chunks: List[RetrievedChunk], history: List[Message]) -> str:
        context_str = self.build_context_string(chunks)
        history_str = self.build_history_string(history)
        return self.rag_template.format(
            context=context_str,
            chat_history=history_str,
            question=question
        )


class CitationBuilder:
    @staticmethod
    def build_citations(message_id: UUID, chunks: List[RetrievedChunk]) -> List[Citation]:
        citations = []
        for idx, chunk in enumerate(chunks):
            citation = Citation(
                message_id=message_id,
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                document_name=chunk.document_title,
                page_number=chunk.page_number,
                similarity_score=chunk.similarity_score,
                citation_order=idx + 1
            )
            citations.append(citation)
        return citations


class RAGOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = Retriever(db)
        self.router = QueryRouter()
        self.evidence_validator = EvidenceValidator()
        self.prompt_builder = PromptBuilder()
        self.citation_builder = CitationBuilder()
        self.ai_provider = get_ai_provider()

    def process_query(
        self,
        question: str,
        history: List[Message] = [],
        collection_id: Optional[UUID] = None,
        department: Optional[str] = None
    ) -> Tuple[str, List[RetrievedChunk]]:
        intent = self.router.classify(question)

        if intent == QueryIntent.GENERAL_CONVERSATION:
            reply = "Hello! I am your official College RAG Assistant. Ask me anything about admissions, courses, fee structures, academic schedules, library policies, or hostel facilities!"
            return reply, []

        if intent == QueryIntent.UNSUPPORTED:
            reply = "I am designed specifically to assist with official college policies, courses, admissions, examinations, fees, and campus services. Please ask a college-related question."
            return reply, []

        # RAG Workflow
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            collection_id=collection_id,
            department=department
        )

        has_evidence = self.evidence_validator.validate(retrieved_chunks)
        if not has_evidence:
            reply = "I couldn't find enough information about that in the college knowledge base. Please try rephrasing your question or contact the relevant college administrative office."
            return reply, []

        prompt = self.prompt_builder.build_prompt(question, retrieved_chunks, history)
        answer = self.ai_provider.generate(prompt, system_instruction=self.prompt_builder.system_prompt)
        return answer, retrieved_chunks

    def stream_query(
        self,
        question: str,
        history: List[Message] = [],
        collection_id: Optional[UUID] = None,
        department: Optional[str] = None
    ) -> Generator[str, None, None]:
        # Format SSE events
        def sse_pack(event_type: str, data_dict: Dict[str, Any]) -> str:
            return f"event: {event_type}\ndata: {json.dumps(data_dict)}\n\n"

        yield sse_pack("message.started", {"status": "started"})
        yield sse_pack("retrieval.started", {"query": question})

        intent = self.router.classify(question)

        if intent == QueryIntent.GENERAL_CONVERSATION:
            yield sse_pack("retrieval.completed", {"chunks_count": 0, "chunks": []})
            yield sse_pack("generation.started", {})
            greeting = "Hello! I am your official College RAG Assistant. Ask me anything about admissions, academic calendars, fee policies, library rules, or campus facilities!"
            yield sse_pack("generation.delta", {"text": greeting})
            yield sse_pack("generation.completed", {"answer": greeting})
            yield sse_pack("citations.completed", {"citations": []})
            yield sse_pack("message.completed", {"status": "completed"})
            return

        if intent == QueryIntent.UNSUPPORTED:
            yield sse_pack("retrieval.completed", {"chunks_count": 0, "chunks": []})
            yield sse_pack("generation.started", {})
            unsupported_msg = "I am designed specifically to assist with official college policies, courses, admissions, examinations, fees, and campus services. Please ask a college-related question."
            yield sse_pack("generation.delta", {"text": unsupported_msg})
            yield sse_pack("generation.completed", {"answer": unsupported_msg})
            yield sse_pack("citations.completed", {"citations": []})
            yield sse_pack("message.completed", {"status": "completed"})
            return

        # Vector Retrieval
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            collection_id=collection_id,
            department=department
        )

        chunk_data = [
            {
                "document_id": str(c.document_id),
                "document_name": c.document_title,
                "chunk_id": str(c.chunk_id),
                "page": c.page_number,
                "similarity": c.similarity_score
            }
            for c in retrieved_chunks
        ]
        yield sse_pack("retrieval.completed", {"chunks_count": len(retrieved_chunks), "chunks": chunk_data})

        has_evidence = self.evidence_validator.validate(retrieved_chunks)
        if not has_evidence:
            yield sse_pack("generation.started", {})
            not_found_msg = "I couldn't find enough information about that in the college knowledge base. Please try rephrasing your question or contact the relevant college administrative office."
            yield sse_pack("generation.delta", {"text": not_found_msg})
            yield sse_pack("generation.completed", {"answer": not_found_msg})
            yield sse_pack("citations.completed", {"citations": []})
            yield sse_pack("message.completed", {"status": "completed"})
            return

        # Generation Phase
        yield sse_pack("generation.started", {})
        prompt = self.prompt_builder.build_prompt(question, retrieved_chunks, history)
        accumulated_answer = ""

        for token in self.ai_provider.generate_stream(prompt, system_instruction=self.prompt_builder.system_prompt):
            accumulated_answer += token
            yield sse_pack("generation.delta", {"text": token})

        yield sse_pack("generation.completed", {"answer": accumulated_answer})
        yield sse_pack("citations.completed", {"citations": chunk_data})
        yield sse_pack("message.completed", {"status": "completed"})
