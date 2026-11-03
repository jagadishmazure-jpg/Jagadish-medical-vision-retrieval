# Threat model (summary)

| Threat | Mitigation in this scaffold | Residual risk |
|---|---|---|
| PII leaking into a released summary | Redaction of email, phone, SSN, card numbers before release | Free-text PII in unusual formats may evade regexes |
| Agent releasing without human approval | HumanGate is the only release path; bypass/reject/absent tests | No authentication of the approver's identity in-process |
| Ambiguous consent misread as approval | Self-contradicting consent blocks release | Natural-language consent parsing is heuristic, not legal consent |
| Audit log tampering | Hash-chained entries; verification test | Log is in-memory; persistent tamper-evident storage is planned, not built |
| Misreading retrieval as diagnosis | Disclaimer on every explanation; hard boundaries in README | A reader may still misuse output — hence the human gate |
| Prompt / data injection via notes | Notes are treated as data, never as instructions; no LLM is called | N/A in this stdlib scaffold |

No real medical data, no network access, and no external model calls exist in
this project, which bounds the blast radius to the synthetic corpus itself.
