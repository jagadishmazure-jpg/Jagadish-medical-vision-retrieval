"""Cost/budget validation: negative inputs are always rejected."""


def validate_search_budget(top_k: int, cost_limit: float) -> None:
    if top_k < 0:
        raise ValueError("top_k must not be negative")
    if cost_limit < 0:
        raise ValueError("cost_limit must not be negative")


def estimate_query_cost(num_cases_scanned: int, cost_per_case: float = 0.01) -> float:
    if num_cases_scanned < 0:
        raise ValueError("num_cases_scanned must not be negative")
    if cost_per_case < 0:
        raise ValueError("cost_per_case must not be negative")
    return round(num_cases_scanned * cost_per_case, 4)
