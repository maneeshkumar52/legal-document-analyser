"""Cross-contract comparison analysis."""
import json
import structlog
from typing import List
from openai import AsyncAzureOpenAI
from src.config import get_settings
from src.models import ComparisonResult
from src.retriever import TwoLevelRetriever

logger = structlog.get_logger(__name__)

COMPARE_PROMPT = """You are a legal analyst comparing clauses across multiple contracts.
For each contract provided, summarise the key terms for the specified clause type.
Then identify the main differences between the contracts.
Respond with JSON: {"comparison": {"contract_id_1": "summary", "contract_id_2": "summary"}, "differences": ["diff1", "diff2"], "recommendation": "advice"}"""


class ContractComparator:
    """Compares terms across multiple legal documents."""

    def __init__(self) -> None:
        s = get_settings()
        self.client = AsyncAzureOpenAI(azure_endpoint=s.azure_openai_endpoint, api_key=s.azure_openai_api_key, api_version=s.azure_openai_api_version, max_retries=3)
        self.settings = s
        self.retriever = TwoLevelRetriever()

    async def compare_terms(self, contract_ids: List[str], clause_type: str) -> ComparisonResult:
        """
        Compare a specific clause type across multiple contracts.

        Args:
            contract_ids: List of contract identifiers to compare.
            clause_type: Type of clause to compare (e.g. 'liability', 'payment', 'termination').

        Returns:
            ComparisonResult with comparison matrix and differences.
        """
        logger.info("contract_comparison_started", contracts=contract_ids, clause_type=clause_type)

        contract_texts = {}
        for cid in contract_ids:
            chunks = await self.retriever.search(clause_type, contract_id=cid, top_k=4)
            contract_texts[cid] = "\n\n".join(c.content for c in chunks[:3]) or "No relevant clauses found."

        contracts_context = "\n\n---\n\n".join(
            f"CONTRACT: {cid}\n{text}" for cid, text in contract_texts.items()
        )

        try:
            resp = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": COMPARE_PROMPT},
                    {"role": "user", "content": f"Clause Type: {clause_type}\n\n{contracts_context}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1200,
            )
            parsed = json.loads(resp.choices[0].message.content)
            return ComparisonResult(
                contract_ids=contract_ids,
                clause_type=clause_type,
                comparison=parsed.get("comparison", {}),
                differences=parsed.get("differences", []),
                recommendation=parsed.get("recommendation", ""),
            )
        except Exception as exc:
            logger.error("comparison_failed", error=str(exc))
            return ComparisonResult(
                contract_ids=contract_ids,
                clause_type=clause_type,
                comparison={cid: "Analysis failed" for cid in contract_ids},
                differences=["Comparison could not be completed"],
                recommendation="Please review contracts manually.",
            )
