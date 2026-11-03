import pytest

from medical_vision_retrieval import Approval, AuditLog, HumanGate, parse_consent, redact_pii
from medical_vision_retrieval.brand import BLOCKLIST_HASHES, contains_blocked


def _gate():
    return HumanGate()


def test_redact_email():
    out = redact_pii("contact jane.doe@example.com please")
    assert "jane.doe@example.com" not in out and "REDACTED:EMAIL" in out


def test_redact_phone():
    out = redact_pii("call 555-123-4567 now")
    assert "555-123-4567" not in out and "REDACTED:PHONE" in out


def test_redact_ssn():
    out = redact_pii("ssn 123-45-6789 here")
    assert "123-45-6789" not in out and "REDACTED:SSN" in out


def test_redact_card_number():
    out = redact_pii("card 4111 1111 1111 1111 charged")
    assert "4111" not in out and "REDACTED:CARD" in out


def test_redact_clean_text_unchanged():
    assert redact_pii("patchy lower lobe opacity") == "patchy lower lobe opacity"


def test_redact_all_four_in_one_note():
    text = "jane.doe@example.com 555-123-4567 123-45-6789 4111 1111 1111 1111"
    out = redact_pii(text)
    assert all(tag in out for tag in ("REDACTED:EMAIL", "REDACTED:PHONE", "REDACTED:SSN", "REDACTED:CARD"))


def test_gate_releases_with_valid_approval_and_consent():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    result = _gate().release("CASE-001 summary", approval, parse_consent("yes, release it"), 0.9)
    assert result.released is True
    assert approval.used is True


def test_gate_bypass_no_approval_blocked():
    result = _gate().release("summary", None, parse_consent("yes"), 0.9)
    assert result.released is False


def test_gate_reject_expired_approval():
    from datetime import datetime, timedelta, timezone
    approval = Approval("Dr Priya Nair", "release-case-summary", datetime.now(timezone.utc) - timedelta(minutes=1))
    result = _gate().release("summary", approval, parse_consent("yes"), 0.9)
    assert result.released is False


def test_gate_reject_used_approval():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    approval.used = True
    assert _gate().release("summary", approval, parse_consent("yes"), 0.9).released is False


def test_gate_reject_wrong_scope():
    approval = Approval.fresh("Dr Priya Nair", "some-other-scope")
    assert _gate().release("summary", approval, parse_consent("yes"), 0.9).released is False


def test_gate_reject_blank_approver():
    approval = Approval.fresh("   ", "release-case-summary")
    assert _gate().release("summary", approval, parse_consent("yes"), 0.9).released is False


def test_gate_absent_consent_blocked():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    assert _gate().release("summary", approval, parse_consent("hello"), 0.9).released is False


def test_gate_denied_consent_blocked():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    assert _gate().release("summary", approval, parse_consent("no, do not release"), 0.9).released is False


def test_gate_self_contradicting_consent_blocked():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    decision = parse_consent("yes, wait, no")
    assert decision.status == "ambiguous"
    assert _gate().release("summary", approval, decision, 0.9).released is False


def test_gate_low_confidence_requires_senior():
    reviewer = Approval.fresh("Dr Priya Nair", "release-case-summary", role="reviewer")
    assert _gate().release("summary", reviewer, parse_consent("yes"), 0.3).released is False
    senior = Approval.fresh("Dr Arjun Rao", "release-case-summary", role="senior")
    assert _gate().release("summary", senior, parse_consent("yes"), 0.3).released is True


def test_gate_single_use_second_release_blocked():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    gate = _gate()
    assert gate.release("s1", approval, parse_consent("yes"), 0.9).released is True
    assert gate.release("s2", approval, parse_consent("yes"), 0.9).released is False


def test_consent_variants():
    assert parse_consent("yes").status == "approved"
    assert parse_consent("no").status == "denied"
    assert parse_consent("hello there").status == "absent"
    assert parse_consent("yes, wait, no").status == "ambiguous"
    assert parse_consent("approve, then hold").status == "ambiguous"


def test_audit_chain_verifies():
    log = AuditLog()
    log.append("query")
    log.append("gate released=True")
    assert log.verify_chain() is True
    assert len(log.entries) == 2


def test_audit_chain_detects_tamper():
    log = AuditLog()
    log.append("query")
    log.append("gate released=True")
    tampered = log.entries[0]
    object.__setattr__(tampered, "payload", "forged")
    assert log.verify_chain() is False


def test_audit_genesis_link():
    log = AuditLog()
    first = log.append("first")
    assert first.prev_hash == "GENESIS"
    assert first.index == 0


def test_brand_blocklist_non_empty():
    assert len(BLOCKLIST_HASHES) > 0
    assert all(len(h) == 64 for h in BLOCKLIST_HASHES)


def test_brand_check_flags_sentinel_and_passes_clean():
    assert contains_blocked("see sentinel-blocked-term-alpha here") is True
    assert contains_blocked("patchy lower lobe opacity") is False
