"""Human gate: named-person, single-use, scoped, expiring approvals."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .consent import ConsentDecision

LOW_CONFIDENCE_THRESHOLD = 0.5


@dataclass
class Approval:
    approver: str  # named person, never a role-only or blank value
    scope: str  # e.g. "release-case-summary"
    expires_at: datetime
    role: str = "reviewer"
    used: bool = False

    @classmethod
    def fresh(cls, approver: str, scope: str, role: str = "reviewer",
              minutes: int = 60) -> "Approval":
        return cls(approver, scope,
                   datetime.now(timezone.utc) + timedelta(minutes=minutes), role)

    def is_valid(self, scope: str, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return bool(self.approver.strip()) and not self.used \
            and self.scope == scope and now < self.expires_at


@dataclass(frozen=True)
class GateResult:
    released: bool
    reason: str


class HumanGate:
    """No case summary is released without a valid approval + approved consent.

    Low-confidence summaries additionally require a senior approver.
    Bypass (no approval), reject (expired/used/wrong-scope), and absent
    (no consent) paths are all blocked, never silently passed through.
    """

    SCOPE = "release-case-summary"

    def release(self, summary: str, approval: Approval | None,
                consent: ConsentDecision, confidence: float) -> GateResult:
        if approval is None:
            return GateResult(False, "blocked: no approval (bypass path)")
        if consent.status == "absent":
            return GateResult(False, "blocked: consent absent")
        if consent.status == "ambiguous":
            return GateResult(False, "blocked: self-contradicting consent")
        if consent.status != "approved":
            return GateResult(False, "blocked: consent not approved")
        if not approval.is_valid(self.SCOPE):
            return GateResult(False, "blocked: approval invalid, expired, used, or wrong scope")
        if confidence < LOW_CONFIDENCE_THRESHOLD and approval.role != "senior":
            return GateResult(False, "blocked: low confidence requires senior approver")
        approval.used = True
        return GateResult(True, f"released: {summary}")
