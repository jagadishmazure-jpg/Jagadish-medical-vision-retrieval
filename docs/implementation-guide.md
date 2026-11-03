# Implementation guide

## Run

```bash
python3 -m pytest tests/ -q
python3 scripts/demo.py
```

Requires only Python 3.10+ and pytest. No third-party packages, no `.venv`.

## Extend the corpus

Add a `SyntheticCase` row in `store.py` with invented pattern tokens and a
teaching category. Keep categories fictional and never use real patient data.
Embeddings are derived automatically from the tokens.

## Change the hybrid weights

`SearchQuery(image_weight=..., text_weight=...)` controls the blend. Weights
must not be negative; the agent raises `ValueError` otherwise.

## Add a new gate rule

Add the check in `HumanGate.release` and a test for each path: the path that
passes, the path that is rejected, and the path where the input is absent.
Low-confidence and self-contradicting-consent cases must keep their own tests.
