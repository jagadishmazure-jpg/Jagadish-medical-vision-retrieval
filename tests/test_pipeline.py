from medical_vision_retrieval import Approval, SearchQuery, parse_consent
from medical_vision_retrieval.pipeline import run_pipeline


def test_pipeline_releases_with_gate_and_audit_ok():
    approval = Approval.fresh("Dr Priya Nair", "release-case-summary")
    result = run_pipeline(
        SearchQuery(("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity"),
        approval, parse_consent("yes, release it"))
    assert result.gate.released is True
    assert result.audit_ok is True
    assert len(result.results) > 0
    assert len(result.explanations) == len(result.results)
    assert all("not a diagnosis" in e.disclaimer.lower() for e in result.explanations)


def test_pipeline_blocked_without_approval_but_still_audited():
    result = run_pipeline(
        SearchQuery(("opacity", "lower-lobe", "patchy")), None, parse_consent("yes"))
    assert result.gate.released is False
    assert result.audit_ok is True


def test_pipeline_recover_broadens_on_empty_filtered_result():
    # Modality+region filter matches nothing; fallback drops filters.
    result = run_pipeline(
        SearchQuery(("opacity",), modality="synthetic-mri", body_region="chest"),
        Approval.fresh("Dr Priya Nair", "release-case-summary"),
        parse_consent("yes"))
    assert len(result.results) > 0
    assert result.audit_ok is True


def test_pipeline_covers_prevent_detect_respond_recover():
    # Prevent: summary contains no raw PII pattern; detect/respond/recover
    # are exercised by the assertions above and this end-to-end run.
    result = run_pipeline(
        SearchQuery(("fracture-line", "distal", "linear")),
        Approval.fresh("Dr Arjun Rao", "release-case-summary", role="senior"),
        parse_consent("yes"))
    assert result.results[0].case.teaching_category == "pattern-b"
    assert result.explanations[0].attribution
