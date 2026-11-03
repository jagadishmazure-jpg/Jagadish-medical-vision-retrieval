from medical_vision_retrieval import (
    ExplainabilityAgent, RetrievalAgent, SearchQuery, ValidationAgent, build_demo_corpus,
)


def _agent():
    return RetrievalAgent(build_demo_corpus())


def test_explanation_has_confidence_attribution_trace():
    agent = _agent()
    result = agent.search(SearchQuery(("opacity", "lower-lobe", "patchy")))[0]
    expl = ExplainabilityAgent().explain(result)
    assert expl.case_id == result.case.case_id
    assert 0.0 <= expl.confidence <= 1.0
    assert expl.attribution
    assert len(expl.trace) == 5


def test_explanation_disclaimer_states_not_a_diagnosis():
    agent = _agent()
    result = agent.search(SearchQuery(("opacity", "lower-lobe", "patchy")))[0]
    expl = ExplainabilityAgent().explain(result)
    assert "not a diagnosis" in expl.disclaimer.lower()


def test_explanation_trace_mentions_scores():
    agent = _agent()
    result = agent.search(SearchQuery(("opacity", "lower-lobe", "patchy")))[0]
    trace = " ".join(ExplainabilityAgent().explain(result).trace)
    assert "image score" in trace and "text score" in trace


def test_validation_precision_at_3_on_demo_queries():
    agent = _agent()
    queries = [
        (SearchQuery(("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity"), "pattern-a"),
        (SearchQuery(("fracture-line", "distal", "linear"), "linear distal fracture"), "pattern-b"),
        (SearchQuery(("effusion", "joint-space", "fluid"), "joint fluid effusion"), "pattern-c"),
    ]
    report = ValidationAgent(agent).evaluate(queries, k=3)
    assert report.num_queries == 3
    assert report.k == 3
    assert report.precision_at_k == 1.0
    assert report.attribution_coverage == 1.0


def test_validation_precision_degrades_with_wrong_labels():
    agent = _agent()
    queries = [(SearchQuery(("opacity", "lower-lobe", "patchy")), "pattern-c")]
    report = ValidationAgent(agent).evaluate(queries, k=3)
    assert report.precision_at_k == 0.0


def test_validation_k_must_be_positive():
    import pytest
    agent = _agent()
    with pytest.raises(ValueError):
        ValidationAgent(agent).evaluate([], k=0)


def test_validation_empty_queries_zero_scores():
    report = ValidationAgent(_agent()).evaluate([], k=3)
    assert report.precision_at_k == 0.0
    assert report.attribution_coverage == 0.0
