# Distilled notes: vision-language retrieval for synthetic medical scans

Notes on how this project works.

## The problem in one paragraph

A clinician or researcher looking at an unusual scan often wants prior similar
cases: same modality, same region, same visual pattern, described in similar
words. Text search alone misses visual similarity; image search alone misses
the written context. Combining both, then explaining why each case matched,
makes the result checkable by a human instead of a black-box ranking.

## Key ideas

- **Simulated domain embeddings.** In this scaffold, a case's "image" is a
  deterministic vector built from its invented pattern tokens. Cases sharing
  tokens land close together. This stands in for a real vision encoder while
  keeping the project offline, reproducible, and free of real scans.
- **Hybrid scoring.** Image similarity and text overlap are weighted and
  combined, so a case that matches on both signals outranks one matching on
  only one. Metadata filters (modality, body region) narrow before ranking.
- **Explainability as a first-class output.** Every result carries a confidence
  score, the shared tokens that drove the match (attribution), and a step-by-step
  trace of how the score was formed. If the attribution is empty or generic,
  that itself is visible — attribution coverage measures it.
- **Clinical validation metrics, not generic RAG scores.** Precision@k against
  known synthetic teaching categories answers "did we retrieve the right
  group?" Attribution coverage answers "can we say why?" Neither is a claim
  about diagnostic accuracy, and neither should be read as one.
- **Human gate before release.** Retrieval is low-risk; release is the risky
  step. The gate therefore checks a named, single-use, scoped, unexpired
  approval plus unambiguous consent, and escalates low-confidence results to a
  senior approver. Self-contradicting consent ("yes, wait, no") is treated as
  ambiguous and blocks release.
- **Governance by construction.** Redaction happens before release text is
  formed, and every query and gate decision enters a hash-chained audit log so
  later tampering is detectable.

## What this deliberately does not do

It does not diagnose, triage real patients, read real images, or store real
records. Those would need clinical validation, regulated data handling, and
expert oversight far beyond a portfolio scaffold.
