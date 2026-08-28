import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.config import settings
from app.services.ingestion.parsers import ParsedDocument


class GeneratedChunk(BaseModel):
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    token_count: int
    metadata: Dict[str, Any] = {}


class StructureAwareChunker:
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def estimate_tokens(self, text: str) -> int:
        # Standard approximation: ~4 characters per token
        return max(1, len(text) // 4)

    def chunk_document(self, parsed_doc: ParsedDocument) -> List[GeneratedChunk]:
        chunks: List[GeneratedChunk] = []
        chunk_index = 0

        for page in parsed_doc.pages:
            page_text = page.text.strip()
            if not page_text:
                continue

            # Split by double newline (paragraphs) or sentences
            paragraphs = [p.strip() for p in re.split(r'\n\s*\n', page_text) if p.strip()]
            current_chunk_text = ""

            for para in paragraphs:
                # If paragraph alone exceeds chunk size, split by sentences
                if len(para) > self.chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if len(current_chunk_text) + len(sent) + 1 > self.chunk_size and current_chunk_text:
                            chunks.append(
                                GeneratedChunk(
                                    chunk_index=chunk_index,
                                    content=current_chunk_text.strip(),
                                    page_number=page.page_number,
                                    section_title=page.section_title,
                                    token_count=self.estimate_tokens(current_chunk_text),
                                    metadata={"page": page.page_number}
                                )
                            )
                            chunk_index += 1
                            # Retain overlap
                            overlap_start = max(0, len(current_chunk_text) - self.chunk_overlap)
                            current_chunk_text = current_chunk_text[overlap_start:].strip() + " " + sent
                        else:
                            current_chunk_text = (current_chunk_text + " " + sent).strip()
                else:
                    if len(current_chunk_text) + len(para) + 2 > self.chunk_size and current_chunk_text:
                        chunks.append(
                            GeneratedChunk(
                                chunk_index=chunk_index,
                                content=current_chunk_text.strip(),
                                page_number=page.page_number,
                                section_title=page.section_title,
                                token_count=self.estimate_tokens(current_chunk_text),
                                metadata={"page": page.page_number}
                            )
                        )
                        chunk_index += 1
                        overlap_start = max(0, len(current_chunk_text) - self.chunk_overlap)
                        current_chunk_text = current_chunk_text[overlap_start:].strip() + "\n\n" + para
                    else:
                        current_chunk_text = (current_chunk_text + "\n\n" + para).strip() if current_chunk_text else para

            if current_chunk_text:
                chunks.append(
                    GeneratedChunk(
                        chunk_index=chunk_index,
                        content=current_chunk_text.strip(),
                        page_number=page.page_number,
                        section_title=page.section_title,
                        token_count=self.estimate_tokens(current_chunk_text),
                        metadata={"page": page.page_number}
                    )
                )
                chunk_index += 1

        return chunks
