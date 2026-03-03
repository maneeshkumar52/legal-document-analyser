"""Index legal documents into Azure AI Search with hierarchical chunks."""
import sys, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import get_settings
from src.hierarchical_chunker import HierarchicalChunker


def main():
    settings = get_settings()
    from openai import AzureOpenAI
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex, SimpleField, SearchableField, SearchField,
        SearchFieldDataType, VectorSearch, HnswAlgorithmConfiguration,
        VectorSearchProfile, SemanticConfiguration, SemanticSearch,
        SemanticPrioritizedFields, SemanticField,
    )
    from azure.core.credentials import AzureKeyCredential

    cred = AzureKeyCredential(settings.azure_search_api_key)
    idx_client = SearchIndexClient(endpoint=settings.azure_search_endpoint, credential=cred)
    search_client = SearchClient(endpoint=settings.azure_search_endpoint, index_name=settings.azure_search_index_name, credential=cred)
    oai = AzureOpenAI(azure_endpoint=settings.azure_openai_endpoint, api_key=settings.azure_openai_api_key, api_version=settings.azure_openai_api_version)

    # Create index with hierarchical fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="section", type=SearchFieldDataType.String),
        SimpleField(name="chunk_type", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="parent_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="contract_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="document_title", type=SearchFieldDataType.String),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, vector_search_dimensions=3072, vector_search_profile_name="myHnsw"),
    ]
    vs = VectorSearch(algorithms=[HnswAlgorithmConfiguration(name="myHnsw")], profiles=[VectorSearchProfile(name="myHnsw", algorithm_configuration_name="myHnsw")])
    sc = SemanticConfiguration(name="default", prioritized_fields=SemanticPrioritizedFields(content_fields=[SemanticField(field_name="content")]))
    idx_client.create_or_update_index(SearchIndex(name=settings.azure_search_index_name, fields=fields, vector_search=vs, semantic_search=SemanticSearch(configurations=[sc])))

    chunker = HierarchicalChunker()
    contracts_dir = Path(__file__).parent / "sample_contracts"
    docs_to_index = []

    for f in contracts_dir.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        contract_id = f.stem.replace("_", "-")
        chunks = chunker.chunk(text, contract_id=contract_id, document_title=f.stem.replace("_", " ").title())
        for chunk in chunks:
            emb = oai.embeddings.create(input=chunk.content[:500], model=settings.azure_openai_embedding_deployment).data[0].embedding
            docs_to_index.append({
                "id": chunk.id,
                "content": chunk.content,
                "section": chunk.section,
                "chunk_type": chunk.chunk_type,
                "parent_id": chunk.parent_id or "",
                "contract_id": chunk.contract_id,
                "document_title": chunk.document_title,
                "content_vector": emb,
            })

    if docs_to_index:
        search_client.upload_documents(docs_to_index)
        print(f"Indexed {len(docs_to_index)} chunks from {contracts_dir}")


if __name__ == "__main__":
    main()
