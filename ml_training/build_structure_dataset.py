import pandas as pd
from pymongo import MongoClient
from services.structure.structure_analyzer import StructureAnalyzer


def build_structure_dataset():

    client = MongoClient("mongodb://localhost:27017")
    db = client["code_audit"]

    repos = db["repos"]
    analyzer = StructureAnalyzer()

    rows = []

    for repo in repos.find():

        repo_path = repo["url"]

        metrics = analyzer.analyze(repo_path)

        if not metrics:
            continue

        # Use repo risk score as label
        summary = db["summaries"].find_one({"repo_id": str(repo["_id"])})

        if not summary:
            continue

        health_score = summary.get("overall_score", 100)

        structure_risk = 1 - (health_score / 100)

        row = {
            **metrics,
            "structure_risk": structure_risk
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    df.to_csv("ml_training/structure_dataset.csv", index=False)

    print("Structure dataset saved.")
    print("Samples:", len(df))


if __name__ == "__main__":
    build_structure_dataset()