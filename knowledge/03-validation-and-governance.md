# Validation and governance notes

## Validation design

- **Labels are teaching categories, not diagnoses.** `pattern-a`, `pattern-b`,
  and `pattern-c` group synthetic cases by invented pattern. Precision@k then
  measures retrieval grouping, nothing clinical.
- **Small-sample honesty.** With 12 cases and 3 queries, precision@3 = 1.0 is
  a regression signal that the ranking logic works on its own fixture set.
  It must not be quoted as accuracy, sensitivity, or any clinical metric.
- **Attribution coverage** is the share of explained results carrying at
  least one attribution token and a non-empty trace. A system can rank well
  while explaining poorly; this metric catches that gap.

## Governance design

- **Least privilege by default.** Agents have no network, file, or clinical
  system access; they operate on an in-memory synthetic corpus.
- **Human in the loop at the release boundary.** Nothing is released on an
  agent's say-so alone; the gate is the only release path in `pipeline.py`.
- **Auditability.** Query, fallback, and gate decisions are hash-chained, so a
  later edit to any entry invalidates verification of the whole chain.
- **PII minimisation.** Redaction runs before summary text is assembled, and
  the redaction checklist explicitly covers card numbers and email addresses
  alongside phone numbers and SSNs.
- **Known gaps.** No authentication, no real identity provider, no encrypted
  storage — all out of scope for a local synthetic scaffold and listed as
  planned, not implied.
