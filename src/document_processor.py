"""Document text extraction using Azure Document Intelligence or direct text reading."""
import structlog
from pathlib import Path
from src.config import get_settings

logger = structlog.get_logger(__name__)


class DocumentProcessor:
    """Extracts text from legal documents (PDF via Azure Document Intelligence, or plain text)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    def _get_di_client(self):
        if self._client is None:
            try:
                from azure.ai.formrecognizer import DocumentAnalysisClient
                from azure.core.credentials import AzureKeyCredential
                self._client = DocumentAnalysisClient(
                    endpoint=self.settings.azure_doc_intelligence_endpoint,
                    credential=AzureKeyCredential(self.settings.azure_doc_intelligence_key),
                )
            except Exception:
                self._client = None
        return self._client

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document file.

        For PDF files: uses Azure Document Intelligence.
        For .md/.txt files: reads directly.

        Args:
            file_path: Path to the document.

        Returns:
            Extracted text content.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if path.suffix.lower() in (".md", ".txt"):
            text = path.read_text(encoding="utf-8")
            logger.info("text_extracted_direct", file=path.name, chars=len(text))
            return text

        if path.suffix.lower() == ".pdf":
            client = self._get_di_client()
            if client:
                try:
                    with open(file_path, "rb") as f:
                        poller = client.begin_analyze_document("prebuilt-read", f)
                        result = poller.result()
                    text = "\n".join(p.content for p in result.paragraphs) if result.paragraphs else ""
                    logger.info("pdf_extracted_azure_di", file=path.name, chars=len(text))
                    return text
                except Exception as exc:
                    logger.error("azure_di_failed", error=str(exc))

        # Fallback: try reading as text
        try:
            return path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.error("text_read_failed", file=str(path), error=str(exc))
            return ""
