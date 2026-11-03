"""Demo: hybrid retrieval + explanation + gated release over synthetic cases."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from medical_vision_retrieval import (
    Approval, RetrievalAgent, SearchQuery, ValidationAgent, build_demo_corpus, parse_consent,
)
from medical_vision_retrieval.explain import ExplainabilityAgent
from medical_vision_retrieval.pipeline import run_pipeline

if __name__ == "__main__":
    agent = RetrievalAgent(build_demo_corpus())
    query = SearchQuery(("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity")
    top = agent.search(query)[0]
    print(f"Top match: {top.case.case_id} score={top.score:.2f}")
    print("Explanation:", ExplainabilityAgent().explain(top))
    queries = [
        (SearchQuery(("opacity", "lower-lobe", "patchy"), "patchy lower lobe opacity"), "pattern-a"),
        (SearchQuery(("fracture-line", "distal", "linear"), "linear distal fracture"), "pattern-b"),
        (SearchQuery(("effusion", "joint-space", "fluid"), "joint fluid effusion"), "pattern-c"),
    ]
    print("Validation:", ValidationAgent(agent).evaluate(queries, k=3))
    result = run_pipeline(query, Approval.fresh("Dr Priya Nair", "release-case-summary"),
                          parse_consent("yes, release it"))
    print("Gate released:", result.gate.released, "| audit ok:", result.audit_ok)
    print("Retrieval and explanation only — not a diagnosis. All data synthetic.")
