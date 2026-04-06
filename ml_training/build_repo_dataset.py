# ml_training/build_repo_dataset.py

import os
import pandas as pd
from pymongo import MongoClient


def build_repo_dataset():

    client = MongoClient("mongodb://localhost:27017")
    db = client["code_audit"]  # change if needed

    error_reports = db["error_reports"]
    repos = db["repos"]

    print("Building repo-level dataset...")

    repo_data = {}

    for doc in error_reports.find():

        repo_id = doc["repo_id"]
        metrics = doc.get("metrics", {})
        risk_score = doc.get("risk_score", 0)

        if repo_id not in repo_data:
            repo_data[repo_id] = {
                "total_files": 0,
                "total_issues": 0,
                "security_issues": 0,
                "risk_sum": 0,
                "complexity_sum": 0,
                "duplication_sum": 0,
                "test_sum": 0
            }

        repo_data[repo_id]["total_files"] += 1
        repo_data[repo_id]["total_issues"] += metrics.get("total_issue_count", 0)
        repo_data[repo_id]["security_issues"] += metrics.get("security_issue_count", 0)
        repo_data[repo_id]["risk_sum"] += risk_score
        repo_data[repo_id]["complexity_sum"] += metrics.get("cyclomatic_complexity", 0)
        repo_data[repo_id]["duplication_sum"] += metrics.get("duplication_ratio", 0)
        repo_data[repo_id]["test_sum"] += metrics.get("has_tests", 0)

    rows = []

    for repo_id, data in repo_data.items():

        total_files = data["total_files"]

        if total_files == 0:
            continue

        avg_risk = data["risk_sum"] / total_files
        avg_complexity = data["complexity_sum"] / total_files
        avg_duplication = data["duplication_sum"] / total_files
        test_ratio = data["test_sum"] / total_files
        issue_density = data["total_issues"] / total_files
        security_density = data["security_issues"] / total_files

        rows.append({
            "avg_complexity": avg_complexity,
            "avg_duplication": avg_duplication,
            "test_ratio": test_ratio,
            "issue_density": issue_density,
            "security_density": security_density,
            "avg_risk": avg_risk  # target label
        })

    df = pd.DataFrame(rows)

    output_path = os.path.join(
        os.path.dirname(__file__),
        "repo_dataset.csv"
    )

    df.to_csv(output_path, index=False)

    print("Repo dataset saved:", output_path)
    print("Samples:", len(df))
    print(df.describe())


if __name__ == "__main__":
    build_repo_dataset()