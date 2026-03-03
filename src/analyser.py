"""Contract analysis: clause extraction, obligation detection, risk identification."""
import json
import structlog
from typing import List, Optional
from openai import AsyncAzureOpenAI
from src.config import get_settings
from src.models import ClauseExtraction, Obligation, RiskArea, ContractAnalysis
from src.retriever import TwoLevelRetriever

logger = structlog.get_logger(__name__)

CLAUSE_PROMPT = """You are a legal analyst. Extract specific clauses from the provided contract text.
For each clause found, identify: reference (clause number), clause_type (e.g. liability, payment, termination, confidentiality, IP, warranty), party, content, deadline (if any), penalty (if any).
Respond with JSON array: [{"reference": "...", "clause_type": "...", "party": "...", "content": "...", "deadline": null, "penalty": null}]"""

OBLIGATION_PROMPT = """You are a legal analyst. Extract all obligations from this contract text.
For each obligation: party (who must act), action (what they must do), deadline (when), condition (under what circumstances).
Respond with JSON array: [{"party": "...", "action": "...", "deadline": null, "condition": null}]"""

RISK_PROMPT = """You are a legal risk analyst. Identify risk areas in this contract.
For each risk: category (e.g. financial, operational, legal, reputational), description, severity (high/medium/low), mitigation.
Respond with JSON array: [{"category": "...", "description": "...", "severity": "...", "mitigation": null}]"""


class ContractAnalyser:
    """Extracts clauses, obligations, and risks from legal documents."""

    def __init__(self) -> None:
        s = get_settings()
        self.client = AsyncAzureOpenAI(azure_endpoint=s.azure_openai_endpoint, api_key=s.azure_openai_api_key, api_version=s.azure_openai_api_version, max_retries=3)
        self.settings = s
        self.retriever = TwoLevelRetriever()

    async def _call_llm_json(self, system: str, user: str) -> list:
        try:
            resp = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1500,
            )
            result = json.loads(resp.choices[0].message.content)
            if isinstance(result, list):
                return result
            # Sometimes the LLM wraps in an object key
            for val in result.values():
                if isinstance(val, list):
                    return val
            return []
        except Exception as exc:
            logger.error("llm_json_failed", error=str(exc))
            return []

    async def extract_clauses(self, query: str, contract_id: Optional[str] = None) -> List[ClauseExtraction]:
        """Extract relevant clauses from contract based on query."""
        chunks = await self.retriever.search(query, contract_id=contract_id, top_k=6)
        context = "\n\n".join(c.content for c in chunks[:5])
        raw = await self._call_llm_json(CLAUSE_PROMPT, f"Query: {query}\n\nContract Text:\n{context}")
        clauses = []
        for item in raw:
            try:
                clauses.append(ClauseExtraction(**item))
            except Exception:
                continue
        logger.info("clauses_extracted", count=len(clauses))
        return clauses

    async def detect_obligations(self, contract_id: str) -> List[Obligation]:
        """Detect all obligations in a contract."""
        chunks = await self.retriever.search("obligations duties shall must", contract_id=contract_id, top_k=8)
        context = "\n\n".join(c.content for c in chunks[:6])
        raw = await self._call_llm_json(OBLIGATION_PROMPT, f"Contract Text:\n{context}")
        obligations = []
        for item in raw:
            try:
                obligations.append(Obligation(**item))
            except Exception:
                continue
        logger.info("obligations_detected", count=len(obligations))
        return obligations

    async def identify_risks(self, contract_id: str) -> List[RiskArea]:
        """Identify risk areas in a contract."""
        chunks = await self.retriever.search("liability indemnity termination breach penalty", contract_id=contract_id, top_k=8)
        context = "\n\n".join(c.content for c in chunks[:6])
        raw = await self._call_llm_json(RISK_PROMPT, f"Contract Text:\n{context}")
        risks = []
        for item in raw:
            try:
                risks.append(RiskArea(**item))
            except Exception:
                continue
        logger.info("risks_identified", count=len(risks))
        return risks
