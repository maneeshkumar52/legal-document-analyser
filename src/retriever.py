"""Two-level retrieval: section summaries first, then paragraph detail."""
import structlog
from typing import List, Optional
from openai import AsyncAzureOpenAI
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from src.config import get_settings
from src.models import DocumentChunkModel

logger = structlog.get_logger(__name__)


class TwoLevelRetriever:
    """
    Retrieves legal document content using a two-level strategy:
    1. Search section summaries for coarse matching
    2. Search paragraphs within matched sections for precise retrieval
    """

    def __init__(self) -> None:
        s = get_settings()
        self.settings = s
        self.openai_client = AsyncAzureOpenAI(azure_endpoint=s.azure_openai_endpoint, api_key=s.azure_openai_api_key, api_version=s.azure_openai_api_version)
        self.search_client = SearchClient(endpoint=s.azure_search_endpoint, index_name=s.azure_search_index_name, credential=AzureKeyCredential(s.azure_search_api_key))

    async def _embed(self, text: str) -> List[float]:
        try:
            resp = await self.openai_client.embeddings.create(input=text, model=self.settings.azure_openai_embedding_deployment)
            return resp.data[0].embedding
        except Exception as exc:
            logger.error("embed_failed", error=str(exc))
            return []

    async def search(self, query: str, contract_id: Optional[str] = None, top_k: int = 8) -> List[DocumentChunkModel]:
        """
        Two-level retrieval: section summaries then paragraph detail.

        Args:
            query: Legal query text.
            contract_id: Optional filter to search within a specific contract.
            top_k: Number of results.

        Returns:
            List of relevant document chunks with parent context.
        """
        logger.info("two_level_search_started", query_len=len(query), contract_id=contract_id)
        try:
            embedding = await self._embed(query)

            # Level 1: Search section summaries
            section_filter = "chunk_type eq 'section_summary'"
            if contract_id:
                section_filter += f" and contract_id eq '{contract_id}'"

            search_kwargs = {
                "search_text": query,
                "top": top_k // 2,
                "filter": section_filter,
                "select": ["id", "content", "section", "chunk_type", "parent_id", "contract_id", "document_title"],
            }
            if embedding:
                search_kwargs["vector_queries"] = [VectorizedQuery(vector=embedding, k_nearest_neighbors=top_k // 2, fields="content_vector")]

            section_results = []
            matched_section_ids = []
            async with self.search_client as client:
                async for doc in await client.search(**search_kwargs):
                    section_results.append(DocumentChunkModel(
                        id=doc.get("id", ""),
                        content=doc.get("content", ""),
                        section=doc.get("section", ""),
                        chunk_type=doc.get("chunk_type", "section_summary"),
                        parent_id=doc.get("parent_id"),
                        contract_id=doc.get("contract_id", ""),
                        document_title=doc.get("document_title", ""),
                    ))
                    matched_section_ids.append(doc.get("id", ""))

                # Level 2: Search paragraphs within matched sections
                para_results = []
                if matched_section_ids:
                    section_id_filter = " or ".join(f"parent_id eq '{sid}'" for sid in matched_section_ids[:3])
                    para_filter = f"chunk_type eq 'paragraph' and ({section_id_filter})"
                    if contract_id:
                        para_filter += f" and contract_id eq '{contract_id}'"

                    para_search = dict(search_kwargs)
                    para_search["filter"] = para_filter
                    para_search["top"] = top_k // 2

                    async for doc in await client.search(**para_search):
                        para_results.append(DocumentChunkModel(
                            id=doc.get("id", ""),
                            content=doc.get("content", ""),
                            section=doc.get("section", ""),
                            chunk_type=doc.get("chunk_type", "paragraph"),
                            parent_id=doc.get("parent_id"),
                            contract_id=doc.get("contract_id", ""),
                            document_title=doc.get("document_title", ""),
                        ))

            combined = section_results + para_results
            logger.info("two_level_search_done", sections=len(section_results), paragraphs=len(para_results))
            return combined
        except Exception as exc:
            logger.error("two_level_search_failed", error=str(exc))
            return []
