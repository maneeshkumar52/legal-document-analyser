"""Two-level hierarchical chunking for legal documents."""
import re
from dataclasses import dataclass, field
from typing import List, Optional
import structlog

logger = structlog.get_logger(__name__)

SECTION_HEADERS = re.compile(
    r'^(?:ARTICLE|SECTION|CLAUSE|SCHEDULE|APPENDIX|PART)\s+[\dIVXivx]+[\.\s]',
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class DocumentChunk:
    """A chunk from a legal document with hierarchical metadata."""
    id: str
    content: str
    section: str
    page_number: Optional[int]
    chunk_type: str  # "section_summary" or "paragraph"
    parent_id: Optional[str]
    contract_id: str
    document_title: str


class HierarchicalChunker:
    """
    Two-level chunker for legal documents:
    - Level 1: Section summaries (~1200 chars) — split on ARTICLE/SECTION/CLAUSE headers
    - Level 2: Paragraphs (~400 chars) within each section
    """

    def __init__(self, section_size: int = 1200, paragraph_size: int = 400) -> None:
        self.section_size = section_size
        self.paragraph_size = paragraph_size

    def _split_into_sections(self, text: str) -> List[tuple]:
        """Split document into (heading, body) sections based on legal headers."""
        parts = SECTION_HEADERS.split(text)
        headers = SECTION_HEADERS.findall(text)

        if not headers:
            # No formal headers — treat as single section
            return [("Document", text)]

        sections = []
        for i, header in enumerate(headers):
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((header.strip(), body.strip()))

        if parts[0].strip():
            sections.insert(0, ("Preamble", parts[0].strip()))

        return sections

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split section text into paragraph-sized chunks."""
        paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
        result = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) + 2 <= self.paragraph_size:
                current += ("\n\n" if current else "") + para
            else:
                if current:
                    result.append(current)
                current = para[:self.paragraph_size]
        if current:
            result.append(current)
        return result or [text[:self.paragraph_size]]

    def chunk(self, text: str, contract_id: str, document_title: str) -> List[DocumentChunk]:
        """
        Chunk a legal document into hierarchical sections and paragraphs.

        Args:
            text: Full document text.
            contract_id: Unique identifier for this contract.
            document_title: Title of the contract.

        Returns:
            List of DocumentChunk objects (section_summary + paragraph chunks).
        """
        import uuid
        sections = self._split_into_sections(text)
        all_chunks = []

        for section_heading, section_body in sections:
            if not section_body.strip():
                continue

            section_id = str(uuid.uuid4())
            section_content = f"{section_heading}\n\n{section_body}"[:self.section_size]

            # Level 1: Section summary chunk
            section_chunk = DocumentChunk(
                id=section_id,
                content=section_content,
                section=section_heading,
                page_number=None,
                chunk_type="section_summary",
                parent_id=None,
                contract_id=contract_id,
                document_title=document_title,
            )
            all_chunks.append(section_chunk)

            # Level 2: Paragraph chunks within section
            paragraphs = self._split_paragraphs(section_body)
            for para_text in paragraphs:
                if len(para_text.strip()) < 30:
                    continue
                para_chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    content=para_text,
                    section=section_heading,
                    page_number=None,
                    chunk_type="paragraph",
                    parent_id=section_id,
                    contract_id=contract_id,
                    document_title=document_title,
                )
                all_chunks.append(para_chunk)

        logger.info("document_chunked", contract_id=contract_id, total_chunks=len(all_chunks), sections=len(sections))
        return all_chunks
