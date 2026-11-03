"""Consent parsing, including self-contradicting consent.

"yes, wait, no" is ambiguous by design: an approval followed in the same
exchange by a retraction must never be read as approval.
"""
from __future__ import annotations

from dataclasses import dataclass

_APPROVE = ("yes", "approve", "approved", "go ahead", "release", "ok")
_RETRACT = ("wait", "no", "stop", "hold", "not yet", "cancel", "do not")


@dataclass(frozen=True)
class ConsentDecision:
    status: str  # "approved" | "denied" | "absent" | "ambiguous"
    reason: str


def parse_consent(transcript: str) -> ConsentDecision:
    text = transcript.lower()
    approved = any(word in text for word in _APPROVE)
    retracted = any(word in text for word in _RETRACT)
    if approved and retracted:
        return ConsentDecision("ambiguous", "approval and retraction both present")
    if retracted:
        return ConsentDecision("denied", "retraction present")
    if approved:
        return ConsentDecision("approved", "approval present")
    return ConsentDecision("absent", "no consent signal present")
