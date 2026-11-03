"""Deterministic simulated image embeddings.

No image model is loaded and no real scan is processed. A simulated
vector is built from the synthetic case's pattern tokens so that cases
sharing visual patterns are near each other and unrelated cases are far
apart. This makes retrieval behaviour testable offline with stdlib only.
"""
from __future__ import annotations

import hashlib
import math

DIM = 32


def _token_vector(token: str) -> list[float]:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    vec = [0.0] * DIM
    # Two stable positions per token give overlap between shared tokens
    # and near-orthogonality between unrelated tokens.
    vec[digest[0] % DIM] += 1.0
    vec[digest[1] % DIM] += 0.5
    return vec


def simulated_embedding(pattern_tokens: tuple[str, ...]) -> tuple[float, ...]:
    """Return a unit-normalised simulated embedding for pattern tokens."""
    vec = [0.0] * DIM
    for token in pattern_tokens:
        for i, value in enumerate(_token_vector(token)):
            vec[i] += value
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return tuple(vec)
    return tuple(v / norm for v in vec)


def cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Cosine similarity in [0, 1] for non-negative simulated vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (na * nb)))
