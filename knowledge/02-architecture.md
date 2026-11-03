# Architecture

```mermaid
flowchart TB
    subgraph Prevent
        RED[PII redaction<br/>email, phone, SSN, card]
    end
    subgraph Detect
        RET[RetrievalAgent<br/>simulated embeddings + text overlap<br/>modality / region filters]
    end
    subgraph Respond
        EXP[ExplainabilityAgent<br/>confidence, attribution, trace]
        GATE[HumanGate<br/>named, single-use, scoped, expiring]
    end
    subgraph Recover
        FB[Fallback: drop metadata filters<br/>on empty result]
    end
    subgraph Governance
        AUD[Hash-chained audit log]
        CON[Consent parser<br/>approved / denied / absent / ambiguous]
    end
    subgraph Measurement
        VAL[ValidationAgent<br/>precision@k, attribution coverage]
    end
    Q[Synthetic query] --> RED --> RET --> EXP --> GATE --> OUT[Released summary]
    RET --> FB --> EXP
    GATE --> AUD
    RET --> VAL
    CON --> GATE
```

## Component notes

- `medical_vision_retrieval/embeddings.py` — deterministic simulated vectors,
  cosine similarity. No model is loaded.
- `store.py` — 12 synthetic cases, 3 teaching categories, fictional labels only.
- `search.py` — `RetrievalAgent`: hybrid scoring + metadata filtering.
- `explain.py` — `ExplainabilityAgent`: confidence, attribution, 5-step trace.
- `validate.py` — `ValidationAgent`: precision@k and attribution coverage.
- `approval.py` / `consent.py` — human gate and consent parsing.
- `redaction.py` — PII redaction checklist.
- `audit.py` — hash-chained audit log.
- `budget.py` — negative-input rejection for cost/budget values.
- `brand.py` — hashed-blocklist name check.
- `pipeline.py` — the end-to-end agentic flow tying the above together.
