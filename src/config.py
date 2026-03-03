from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    azure_openai_endpoint: str = Field(default="https://your-openai.openai.azure.com/", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="your-key", env="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment: str = Field(default="gpt-4o", env="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_embedding_deployment: str = Field(default="text-embedding-3-large", env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    azure_search_endpoint: str = Field(default="https://your-search.search.windows.net", env="AZURE_SEARCH_ENDPOINT")
    azure_search_api_key: str = Field(default="your-search-key", env="AZURE_SEARCH_API_KEY")
    azure_search_index_name: str = Field(default="legal-documents", env="AZURE_SEARCH_INDEX_NAME")
    azure_doc_intelligence_endpoint: str = Field(default="https://your-docintel.cognitiveservices.azure.com/", env="AZURE_DOC_INTELLIGENCE_ENDPOINT")
    azure_doc_intelligence_key: str = Field(default="your-di-key", env="AZURE_DOC_INTELLIGENCE_KEY")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
