"""Tests for hierarchical chunker."""
import pytest
from src.hierarchical_chunker import HierarchicalChunker

SAMPLE_LEGAL_TEXT = """
PREAMBLE

This Service Agreement ("Agreement") is entered into between Contoso Technology Ltd ("Provider") and Acme Corp ("Client").

ARTICLE 1. DEFINITIONS

1.1 "Services" means the software development and support services described in Schedule A.
1.2 "Confidential Information" means any non-public information disclosed by either party.
1.3 "Deliverables" means all work product created under this Agreement.

ARTICLE 2. PAYMENT TERMS

2.1 Client shall pay Provider £15,000 per month within 30 days of invoice.
2.2 Late payments shall accrue interest at 1.5% per month.
2.3 All fees are exclusive of VAT which shall be added at the prevailing rate.

CLAUSE 3. LIABILITY

3.1 Provider's liability is limited to the fees paid in the preceding 12 months.
3.2 Neither party shall be liable for consequential or indirect losses.
3.3 This limitation does not apply to fraud or wilful misconduct.
"""


def test_chunks_are_created():
    """Chunker should produce chunks from legal text."""
    chunker = HierarchicalChunker()
    chunks = chunker.chunk(SAMPLE_LEGAL_TEXT, contract_id="test-001", document_title="Test Agreement")
    assert len(chunks) > 0


def test_section_summaries_created():
    """Should create at least one section_summary chunk."""
    chunker = HierarchicalChunker()
    chunks = chunker.chunk(SAMPLE_LEGAL_TEXT, contract_id="test-001", document_title="Test Agreement")
    section_chunks = [c for c in chunks if c.chunk_type == "section_summary"]
    assert len(section_chunks) > 0


def test_paragraph_chunks_created():
    """Should create paragraph-level chunks."""
    chunker = HierarchicalChunker()
    chunks = chunker.chunk(SAMPLE_LEGAL_TEXT, contract_id="test-001", document_title="Test Agreement")
    para_chunks = [c for c in chunks if c.chunk_type == "paragraph"]
    assert len(para_chunks) > 0


def test_paragraph_has_parent_id():
    """Paragraph chunks should reference their parent section."""
    chunker = HierarchicalChunker()
    chunks = chunker.chunk(SAMPLE_LEGAL_TEXT, contract_id="test-001", document_title="Test Agreement")
    para_chunks = [c for c in chunks if c.chunk_type == "paragraph"]
    for para in para_chunks:
        assert para.parent_id is not None


def test_contract_id_propagated():
    """All chunks should have the correct contract_id."""
    chunker = HierarchicalChunker()
    chunks = chunker.chunk(SAMPLE_LEGAL_TEXT, contract_id="contract-abc", document_title="Test")
    for chunk in chunks:
        assert chunk.contract_id == "contract-abc"


def test_section_size_respected():
    """Section chunks should not exceed 1200 chars by default."""
    chunker = HierarchicalChunker(section_size=1200)
    chunks = chunker.chunk(SAMPLE_LEGAL_TEXT, contract_id="test-001", document_title="Test")
    for chunk in [c for c in chunks if c.chunk_type == "section_summary"]:
        assert len(chunk.content) <= 1200 + 50  # small tolerance


def test_empty_text_returns_empty_list():
    """Empty text should return no chunks."""
    chunker = HierarchicalChunker()
    chunks = chunker.chunk("", contract_id="empty", document_title="Empty")
    assert len(chunks) == 0


def test_no_headers_treated_as_single_section():
    """Text without formal headers should produce at least one chunk."""
    chunker = HierarchicalChunker()
    plain_text = "This contract is between Party A and Party B. Party A agrees to provide services. Party B agrees to pay within 30 days."
    chunks = chunker.chunk(plain_text, contract_id="plain-001", document_title="Simple Agreement")
    assert len(chunks) >= 1
