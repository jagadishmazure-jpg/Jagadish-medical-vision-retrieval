"""Agentic pipeline: prevent / detect / respond / recover + governance + measurement.

Prevent: PII redaction before any text leaves the system.
Detect: RetrievalAgent finds similar synthetic cases.
Respond: ExplainabilityAgent explains each result; HumanGate holds release.
Recover: empty results fall back to a broader search instead of failing.
Governance: every release decision is hash-chained in the audit log.
Measurement: ValidationAgent scores the run (reported separately).
"""
from __future__ import annotations

from dataclasses import dataclass

from .approval import Approval, GateResult, HumanGate
from .audit import AuditLog
from .consent import ConsentDecision
from .explain import ExplainabilityAgent, Explanation
from .redaction import redact_pii
from .search import RetrievalAgent, SearchQuery
from .store import SyntheticCase, build_demo_corpus


@dataclass(frozen=True)
class PipelineResult:
    results: tuple
    explanations: tuple[Explanation, ...]
    gate: GateResult
    audit_ok: bool


def run_pipeline(query: SearchQuery, approval: Approval | None,
                 consent: ConsentDecision,
                 corpus: list[SyntheticCase] | None = None) -> PipelineResult:
    corpus = corpus if corpus is not None else build_demo_corpus()
    agent = RetrievalAgent(corpus)
    explainer = ExplainabilityAgent()
    audit = AuditLog()
    audit.append(f"query patterns={','.join(query.pattern_tokens)}")
    results = agent.search(query)
    if not results:  # recover: broaden by dropping metadata filters
        results = agent.search(SearchQuery(query.pattern_tokens, query.text, top_k=query.top_k))
        audit.append("fallback: metadata filters dropped after empty result")
    explanations = tuple(explainer.explain(r) for r in results)
    summary = redact_pii("; ".join(f"{e.case_id} score={e.confidence}" for e in explanations))
    gate = HumanGate().release(summary, approval, consent, explanations[0].confidence if explanations else 0.0)
    audit.append(f"gate released={gate.released} reason={gate.reason}")
    return PipelineResult(tuple(results), explanations, gate, audit.verify_chain())
