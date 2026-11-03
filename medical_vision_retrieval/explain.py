"""Explainability: confidence, retrieval attribution, reasoning trace."""
from __future__ import annotations

from dataclasses import dataclass

from .search import SearchResult


@dataclass(frozen=True)
class Explanation:
    case_id: str
    confidence: float
    attribution: tuple[str, ...]
    trace: tuple[str, ...]
    disclaimer: str = (
        "Retrieval and explanation only. This is not a diagnosis, "
        "and no clinical decision should be based on it alone."
    )


class ExplainabilityAgent:
    """Response agent: explains WHY a case was retrieved, in plain steps."""

    def explain(self, result: SearchResult) -> Explanation:
        attribution = result.shared_tokens or ("modality-match",)
        trace = (
            f"1. Compared simulated image embedding (image score {result.image_score:.3f}).",
            f"2. Compared text notes (text score {result.text_score:.3f}).",
            f"3. Combined hybrid score {result.score:.3f} "
            f"from shared patterns: {', '.join(attribution)}.",
            f"4. Applied metadata context: {result.case.modality} / {result.case.body_region}.",
            "5. Returned as a similar synthetic case for human review only.",
        )
        return Explanation(result.case.case_id, round(result.score, 4), attribution, trace)
