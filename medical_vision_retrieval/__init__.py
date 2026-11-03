"""Vision-language retrieval over synthetic medical scans.

Retrieval and explanation only. Never a diagnosis claim. No real
medical data anywhere; every scan and case in this package is synthetic.
"""

from .approval import Approval, HumanGate
from .audit import AuditLog
from .budget import validate_search_budget
from .consent import ConsentDecision, parse_consent
from .explain import ExplainabilityAgent
from .redaction import redact_pii
from .search import RetrievalAgent, SearchQuery, SearchResult
from .store import SyntheticCase, build_demo_corpus
from .validate import ValidationAgent

__all__ = [
    "Approval",
    "AuditLog",
    "ConsentDecision",
    "ExplainabilityAgent",
    "HumanGate",
    "RetrievalAgent",
    "SearchQuery",
    "SearchResult",
    "SyntheticCase",
    "ValidationAgent",
    "build_demo_corpus",
    "parse_consent",
    "redact_pii",
    "validate_search_budget",
]
