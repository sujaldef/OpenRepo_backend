import numpy as np


FEATURE_ORDER = [
    "loc",
    "function_count",
    "avg_function_length",
    "max_function_length",
    "cyclomatic_complexity",
    "max_nesting_depth",
    "total_issue_count",
    "security_issue_count",
    "duplication_ratio",
    "dependency_risk_score",
    "has_tests"
]


def build_feature_vector(metrics: dict):
    """
    Converts metrics dict into ordered numeric vector.
    """

    vector = []

    for key in FEATURE_ORDER:
        vector.append(metrics.get(key, 0))

    return np.array(vector, dtype=float)