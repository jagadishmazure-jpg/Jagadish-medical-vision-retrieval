"""Hybrid image-plus-text retrieval with metadata filtering."""
from __future__ import annotations

import re
from dataclasses import dataclass

from .budget import validate_search_budget
from .embeddings import cosine, simulated_embedding
from .store import SyntheticCase

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def _text_score(query_text: str, case: SyntheticCase) -> float:
    q, c = _tokens(query_text), _tokens(case.text_notes)
    if not q or not c:
        return 0.0
    return len(q & c) / len(q | c)


@dataclass(frozen=True)
class SearchQuery:
    pattern_tokens: tuple[str, ...]
    text: str = ""
    modality: str | None = None
    body_region: str | None = None
    top_k: int = 5
    image_weight: float = 0.6
    text_weight: float = 0.4


@dataclass(frozen=True)
class SearchResult:
    case: SyntheticCase
    score: float
    image_score: float
    text_score: float
    shared_tokens: tuple[str, ...]


class RetrievalAgent:
    """Detection/triage agent: finds similar synthetic cases, never diagnoses."""

    def __init__(self, corpus: list[SyntheticCase]) -> None:
        self.corpus = list(corpus)

    def search(self, query: SearchQuery, cost_limit: float = 100.0) -> list[SearchResult]:
        validate_search_budget(query.top_k, cost_limit)
        if query.image_weight < 0 or query.text_weight < 0:
            raise ValueError("search weights must not be negative")
        qvec = simulated_embedding(query.pattern_tokens)
        results: list[SearchResult] = []
        for case in self.corpus:
            if query.modality is not None and case.modality != query.modality:
                continue
            if query.body_region is not None and case.body_region != query.body_region:
                continue
            image = cosine(qvec, case.embedding)
            text = _text_score(query.text, case) if query.text else 0.0
            score = query.image_weight * image + query.text_weight * text
            shared = tuple(sorted(set(query.pattern_tokens) & set(case.pattern_tokens)))
            results.append(SearchResult(case, score, image, text, shared))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[: query.top_k]
