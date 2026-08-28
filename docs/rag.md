# RAG Pipeline Specification & Deterministic Flow

## Non-Negotiable Grounding Workflow
The **College RAG Assistant** enforces strict evidence retrieval before any answer is synthesized by the LLM:

```
User Query
    │
    ▼
QueryRouter (Classify into COLLEGE_KNOWLEDGE / GENERAL_CONVERSATION / UNSUPPORTED)
    │
    ▼
Retriever (Generate 768-dim query embedding -> pgvector cosine search)
    │
    ▼
EvidenceValidator (Validate cosine similarity >= 0.65 threshold)
    ├── [Insufficient Evidence] ──► "I couldn't find enough information in the college knowledge base."
    │
    ▼
PromptBuilder (Inject system grounding rules + numbered chunk context + history)
    │
    ▼
AnswerGenerator (Stream response using Google Gemini API or Mock provider)
    │
    ▼
CitationBuilder (Map retrieved chunks to source documents, page numbers & confidence)
    │
    ▼
SSE Response Streamer (Emit structured events to frontend)
```

## SSE Event Protocol

| Event Name | Description | Data Payload |
|---|---|---|
| `message.started` | Chat turn initialized | `{"status": "started"}` |
| `retrieval.started` | Query embedding & vector search initiated | `{"query": "..."}` |
| `retrieval.completed` | Vector retrieval finished with top-K chunks | `{"chunks_count": 3, "chunks": [...]}` |
| `generation.started` | Context built, LLM generation started | `{}` |
| `generation.delta` | Streamed text token delta | `{"text": "token"}` |
| `generation.completed` | Complete generated answer text | `{"answer": "full text"}` |
| `citations.completed` | List of citations with page & similarity | `{"citations": [...]}` |
| `message.completed` | Finished message turn | `{"status": "completed"}` |
