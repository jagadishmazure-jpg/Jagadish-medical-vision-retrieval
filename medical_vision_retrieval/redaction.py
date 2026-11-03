"""PII redaction checklist: phone, SSN, card numbers, email addresses."""
from __future__ import annotations

import re

_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[REDACTED:EMAIL]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED:SSN]"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[REDACTED:CARD]"),
    (re.compile(r"\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[REDACTED:PHONE]"),
]


def redact_pii(text: str) -> str:
    """Redact email, SSN, card numbers, then phone numbers, in that order."""
    out = text
    for pattern, replacement in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def contains_pii(text: str) -> bool:
    return redact_pii(text) != text
