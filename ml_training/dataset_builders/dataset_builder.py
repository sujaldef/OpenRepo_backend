# ml_training/dataset_builder.py

import os
import pandas as pd
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "code_audit"
COLLECTION_NAME = "error_reports"

BASE = os.path.dirname(__file__)

OUTPUT_PATH = os.path.join(
    BASE,
    "datasets",
    "dataset.csv"
)


def compute_risk_dimensions(metrics: dict):

    complexity = min(metrics.get("cyclomatic_complexity", 1) / 20, 1)
    issue_density = min(metrics.get("total_issue_count", 0) / 10, 1)
    security_density = min(metrics.get("security_issue_count", 0) / 5, 1)
    duplication = min(metrics.get("duplication_ratio", 0), 1)
    dependency_risk = min(metrics.get("dependency_risk_score", 0), 1)
    has_tests_penalty = 1 - metrics.get("has_tests", 0)

    structural_risk = 0.6 * complexity + 0.4 * issue_density
    security_risk = 0.7 * security_density + 0.3 * dependency_risk
    maintainability_risk = 0.6 * duplication + 0.4 * complexity
    test_risk = has_tests_penalty * complexity

    overall_risk = (
        0.35 * structural_risk +
        0.30 * security_risk +
        0.20 * maintainability_risk +
        0.15 * test_risk
    )

    return {
        "structural_risk": round(min(structural_risk, 1), 4),
        "security_risk": round(min(security_risk, 1), 4),
        "maintainability_risk": round(min(maintainability_risk, 1), 4),
        "test_risk": round(min(test_risk, 1), 4),
        "overall_risk": round(min(overall_risk, 1), 4)
    }


def build_dataset():

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    records = []

    for doc in collection.find({}):

        metrics = doc.get("metrics", {})
        if not metrics:
            continue

        risks = compute_risk_dimensions(metrics)

        record = {
            "loc": metrics.get("loc", 0),
            "function_count": metrics.get("function_count", 0),
            "avg_function_length": metrics.get("avg_function_length", 0),
            "max_function_length": metrics.get("max_function_length", 0),
            "cyclomatic_complexity": metrics.get("cyclomatic_complexity", 1),
            "max_nesting_depth": metrics.get("max_nesting_depth", 0),
            "total_issue_count": metrics.get("total_issue_count", 0),
            "security_issue_count": metrics.get("security_issue_count", 0),
            "duplication_ratio": metrics.get("duplication_ratio", 0),
            "dependency_risk_score": metrics.get("dependency_risk_score", 0),
            "has_tests": metrics.get("has_tests", 0),
            **risks
        }

        records.append(record)

    df = pd.DataFrame(records)
    df = df[df["loc"] < 5000]

    df.to_csv(OUTPUT_PATH, index=False)

    print("Dataset saved:", OUTPUT_PATH)
    print("Total samples:", len(df))


if __name__ == "__main__":
    build_dataset()