import pytest

from medical_vision_retrieval import RetrievalAgent, SearchQuery, build_demo_corpus
from medical_vision_retrieval.budget import estimate_query_cost


@pytest.fixture
def agent():
    return RetrievalAgent(build_demo_corpus())


def test_exact_pattern_match_ranks_first(agent):
    q = SearchQuery(("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity")
    top = agent.search(q)[0]
    assert top.case.case_id in ("CASE-001", "CASE-002")
    assert top.score > 0.5


def test_hybrid_beats_image_only_for_text_match(agent):
    q_img = SearchQuery(("opacity", "lower-lobe", "patchy"), "")
    q_hyb = SearchQuery(("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity")
    assert agent.search(q_hyb)[0].score >= agent.search(q_img)[0].score


def test_metadata_filter_modality(agent):
    q = SearchQuery(("opacity", "lower-lobe", "patchy"), modality="synthetic-ct")
    results = agent.search(q)
    assert results and all(r.case.modality == "synthetic-ct" for r in results)


def test_metadata_filter_body_region(agent):
    q = SearchQuery(("effusion", "joint-space", "fluid"), body_region="knee")
    assert all(r.case.body_region == "knee" for r in agent.search(q))


def test_filter_no_match_returns_empty(agent):
    q = SearchQuery(("opacity",), modality="synthetic-mri", body_region="chest")
    assert agent.search(q) == []


def test_top_k_respected(agent):
    assert len(agent.search(SearchQuery(("opacity",), top_k=2))) == 2


def test_top_k_zero_returns_empty(agent):
    assert agent.search(SearchQuery(("opacity",), top_k=0)) == []


def test_unrelated_pattern_scores_lower(agent):
    same = agent.search(SearchQuery(("opacity", "lower-lobe", "patchy")))[0].score
    other = agent.search(SearchQuery(("effusion", "joint-space", "fluid")))[0].score
    # Same-pattern query must rank a pattern-a case, other-pattern a pattern-c case
    assert agent.search(SearchQuery(("opacity", "lower-lobe", "patchy")))[0].case.teaching_category == "pattern-a"
    assert agent.search(SearchQuery(("effusion", "joint-space", "fluid")))[0].case.teaching_category == "pattern-c"
    assert same > 0 and other > 0


def test_shared_tokens_reported(agent):
    top = agent.search(SearchQuery(("opacity", "lower-lobe", "patchy")))[0]
    assert "opacity" in top.shared_tokens


def test_scores_bounded_0_to_1(agent):
    for r in agent.search(SearchQuery(("opacity", "lower-lobe", "patchy"))):
        assert 0.0 <= r.score <= 1.0
        assert 0.0 <= r.image_score <= 1.0


def test_corpus_size_and_categories():
    corpus = build_demo_corpus()
    assert len(corpus) == 12
    assert {c.teaching_category for c in corpus} == {"pattern-a", "pattern-b", "pattern-c"}


def test_negative_top_k_rejected(agent):
    with pytest.raises(ValueError):
        agent.search(SearchQuery(("opacity",), top_k=-1))


def test_negative_cost_limit_rejected(agent):
    with pytest.raises(ValueError):
        agent.search(SearchQuery(("opacity",)), cost_limit=-5.0)


def test_negative_weights_rejected(agent):
    with pytest.raises(ValueError):
        agent.search(SearchQuery(("opacity",), image_weight=-0.1))


def test_estimate_cost_rejects_negatives():
    with pytest.raises(ValueError):
        estimate_query_cost(-1)
    with pytest.raises(ValueError):
        estimate_query_cost(10, cost_per_case=-0.5)


def test_estimate_cost_value():
    assert estimate_query_cost(12) == 0.12
