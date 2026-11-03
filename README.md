# Jagadish-medical-vision-retrieval

> **Independent, unaffiliated project.** This repository is not affiliated with,
> endorsed by, or connected to any hospital, vendor, or health system. The
> fictional organisation used in examples is **Caldermere Health** — an invented
> name, not a real business. A web search for the exact phrase "Caldermere Health"
> found no matching real business (similar but distinct names such as Caldera
> Medical exist and are unrelated).

## HARD BOUNDARIES — read first

- **Retrieval and explanation only, never a diagnosis claim.** Results are
  similar synthetic cases for human review, with a disclaimer on every explanation.
- **No real medical data anywhere.** All scans, cases, notes, and labels are
  synthetic and invented. No real patient, clinician, or hospital data is used.
- **No clinical decision should be based on this system alone.** A human gate
  must approve before any case summary is released.

## Recruiter summary

Vision-language retrieval over synthetic medical scans: simulated domain image
embeddings combined with text search, metadata filtering, and explainability
(confidence, retrieval attribution, diagnostic-reasoning trace) for each result.
Three agents — retrieval, explainability, validation — plus a human approval gate
cover prevent / detect / respond / recover, governance, and measurement.
Proof: 50 tests pass locally on a 12-case synthetic corpus (see numbers below).

## Purpose and who it is for

For engineers learning how retrieval, explainability, and human gates fit
together in a safety-sensitive domain — without touching real medical data.
It demonstrates agentic structure (agents doing detection, triage, response,
and measurement with human gates) rather than a clinical tool.

## Architecture

See [knowledge/02-architecture.md](knowledge/02-architecture.md) for the full
Mermaid diagram, and [knowledge/01-overview.md](knowledge/01-overview.md) for
distilled notes.

```mermaid
flowchart LR
    Q[Synthetic query] --> R[RetrievalAgent<br/>hybrid image + text search]
    R --> E[ExplainabilityAgent<br/>confidence + attribution + trace]
    E --> G[HumanGate<br/>named, single-use, scoped, expiring approval]
    G --> OUT[Released summary]
    R --> V[ValidationAgent<br/>precision@k + attribution coverage]
    Q --> P[PII redaction]
    G --> A[Hash-chained audit log]
```

## How it works, step by step

1. **Prevent:** free text is PII-redacted (email, phone, SSN, card numbers)
   before it leaves the pipeline.
2. **Detect / triage:** `RetrievalAgent` scores the corpus by hybrid similarity
   (0.6 image + 0.4 text by default) and applies modality / body-region filters.
3. **Respond:** `ExplainabilityAgent` attaches a confidence score, the shared
   pattern tokens that caused the match (attribution), and a 5-step reasoning trace.
4. **Human gate:** `HumanGate` releases a summary only with a named-person,
   single-use, scoped, unexpired approval, approved (non-contradictory) consent,
   and — for low-confidence results — a senior approver.
5. **Recover:** an empty filtered result falls back to a broader unfiltered search.
6. **Governance:** every query and gate decision is appended to a hash-chained
   audit log; tampering breaks chain verification.
7. **Measurement:** `ValidationAgent` scores retrieval against known synthetic
   teaching-category labels.

## Real code and real output

```python
from medical_vision_retrieval import RetrievalAgent, SearchQuery, build_demo_corpus

agent = RetrievalAgent(build_demo_corpus())
top = agent.search(SearchQuery(("opacity", "lower-lobe", "patchy"),
                                "patchy lower lobe opacity"))[0]
print(top.case.case_id, round(top.score, 4))
```

Real output from the local run:

```
CASE-001 0.92
```

## Demo numbers (asserted by tests, synthetic data only)

These are regression checks on a small self-written synthetic set, not quality
or clinical claims. Sample: 12 synthetic cases, 3 validation queries.

| Metric | Value |
|---|---|
| Tests passing (local run) | 50 |
| Synthetic corpus size | 12 cases (3 teaching categories × 4) |
| Top hybrid score, demo query | 0.92 (image 1.0, text 0.8) |
| Precision@3 on 3 synthetic labelled queries | 1.0 |
| Attribution coverage on the same queries | 1.0 |

Run them yourself: `python3 -m pytest tests/ -q` (stdlib only, no venv needed).

## How to run

```bash
python3 -m pytest tests/ -q
python3 scripts/demo.py
```

Offline first; no network, model download, or cloud account is required.

## Guardrails and security controls

- PII redaction checklist: phone, SSN, **card numbers, email addresses**.
- Confirmation/QA gates: bypass (no approval), reject (expired / used /
  wrong-scope / blank approver), and absent-path (no consent) tests, plus
  low-confidence and self-contradicting-consent ("yes, wait, no") tests.
- Approvals: named person, single-use, scoped to `release-case-summary`,
  expiring (default 60 minutes); low-confidence summaries need a senior approver.
- Cost/budget inputs reject negatives (`top_k`, `cost_limit`, cost per case).
- Brand/name check: hashed blocklist, asserted non-empty in tests.
- Hash-chained audit log with tamper-detection test.
- Threat model: see [docs/threat-model.md](docs/threat-model.md).

## Limitations and known failures

- Embeddings are simulated deterministic vectors, not a trained vision model;
  similarity reflects shared invented pattern tokens, not image content.
- The corpus is tiny (12 cases) and hand-built; precision@3 = 1.0 on it proves
  the pipeline works, not that it generalises.
- No real imaging, DICOM handling, or clinical validation is included.
- CI is included in the scaffold but **NOT verified** (unrun in this scaffold-only
  build); do not treat it as CI-green.
- The 8-word overlap check was **NOT run** for this scaffold; original prose
  was written fresh, but no overlap pass is claimed.

## Built / Written-not-run / Planned

| Item | Status |
|---|---|
| RetrievalAgent (hybrid search + metadata filters) | Built, tested |
| ExplainabilityAgent (confidence, attribution, trace) | Built, tested |
| ValidationAgent (precision@k, attribution coverage) | Built, tested |
| HumanGate + consent parsing + PII redaction + hash-chained audit | Built, tested |
| Agentic pipeline (prevent/detect/respond/recover + governance) | Built, tested |
| knowledge/ notes + Mermaid architecture docs | Built |
| CI workflow file (`.github/workflows/ci.yml`) | Written, **not run — CI NOT verified** |
| Real vision model, DICOM support, live deployment | Planned / out of scope |

## Related docs

- [knowledge/01-overview.md](knowledge/01-overview.md)
- [knowledge/02-architecture.md](knowledge/02-architecture.md)
- [knowledge/03-validation-and-governance.md](knowledge/03-validation-and-governance.md)
- [docs/implementation-guide.md](docs/implementation-guide.md)
- [docs/threat-model.md](docs/threat-model.md)
