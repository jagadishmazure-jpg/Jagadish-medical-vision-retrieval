"""Synthetic case corpus. Every record is invented; none is a real patient."""
from __future__ import annotations

from dataclasses import dataclass, field

from .embeddings import simulated_embedding


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    modality: str  # e.g. "synthetic-xray", "synthetic-ct"
    body_region: str
    pattern_tokens: tuple[str, ...]
    text_notes: str
    # A fictional teaching category, NOT a diagnosis.
    teaching_category: str
    embedding: tuple[float, ...] = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "embedding", simulated_embedding(self.pattern_tokens))


def build_demo_corpus() -> list[SyntheticCase]:
    """12 synthetic cases across 3 teaching categories (4 cases each)."""
    specs = [
        ("CASE-001", "synthetic-xray", "chest", ("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity noted", "pattern-a"),
        ("CASE-002", "synthetic-xray", "chest", ("opacity", "lower-lobe", "patchy"), "similar patchy lower lobe pattern", "pattern-a"),
        ("CASE-003", "synthetic-ct", "chest", ("opacity", "lower-lobe", "diffuse"), "diffuse lower lobe opacity", "pattern-a"),
        ("CASE-004", "synthetic-xray", "chest", ("opacity", "upper-lobe", "patchy"), "upper lobe patchy opacity", "pattern-a"),
        ("CASE-005", "synthetic-xray", "wrist", ("fracture-line", "distal", "linear"), "linear distal fracture line", "pattern-b"),
        ("CASE-006", "synthetic-xray", "wrist", ("fracture-line", "distal", "linear"), "same linear distal pattern", "pattern-b"),
        ("CASE-007", "synthetic-ct", "wrist", ("fracture-line", "distal", "comminuted"), "comminuted distal pattern", "pattern-b"),
        ("CASE-008", "synthetic-xray", "wrist", ("fracture-line", "proximal", "linear"), "proximal linear pattern", "pattern-b"),
        ("CASE-009", "synthetic-mri", "knee", ("effusion", "joint-space", "fluid"), "joint fluid effusion pattern", "pattern-c"),
        ("CASE-010", "synthetic-mri", "knee", ("effusion", "joint-space", "fluid"), "same joint fluid pattern", "pattern-c"),
        ("CASE-011", "synthetic-ct", "knee", ("effusion", "joint-space", "swelling"), "joint swelling pattern", "pattern-c"),
        ("CASE-012", "synthetic-mri", "knee", ("effusion", "meniscus", "fluid"), "meniscus fluid pattern", "pattern-c"),
    ]
    return [SyntheticCase(*s) for s in specs]
