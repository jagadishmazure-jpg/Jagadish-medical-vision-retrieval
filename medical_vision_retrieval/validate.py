"""Clinical validation metrics on synthetic labeled cases.

These are retrieval metrics (precision@k, attribution coverage), not
generic text-RAG scores and not clinical accuracy claims: the labels
are fictional teaching categories over synthetic cases.
"""
from __future__ import annotations

from dataclasses import dataclass

from .explain import ExplainabilityAgent
from .search import RetrievalAgent, SearchQuery


@dataclass(frozen=True)
class ValidationReport:
    precision_at_k: float
    attribution_coverage: float
    num_queries: int
    k: int


class ValidationAgent:
    """Measurement agent: scores retrieval against known synthetic labels."""

    def __init__(self, agent: RetrievalAgent) -> None:
        self.agent = agent
        self.explainer = ExplainabilityAgent()

    def evaluate(self, queries: list[tuple[SearchQuery, str]], k: int = 3) -> ValidationReport:
        if k <= 0:
            raise ValueError("k must be positive")
        hits = 0
        total = 0
        attributed = 0
        explained = 0
        for query, expected_category in queries:
            results = self.agent.search(query)[:k]
            for result in results:
                total += 1
                if result.case.teaching_category == expected_category:
                    hits += 1
                explanation = self.explainer.explain(result)
                explained += 1
                if explanation.attribution and explanation.trace:
                    attributed += 1
        precision = hits / total if total else 0.0
        coverage = attributed / explained if explained else 0.0
        return ValidationReport(round(precision, 4), round(coverage, 4), len(queries), k)
