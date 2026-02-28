# services/ml_engine/repo_risk_model.py

import os
import joblib
import numpy as np


class RepoRiskModel:

    def __init__(self):

        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../ml_training/saved_models")
        )

        model_path = os.path.join(base_dir, "repo_risk_model.pkl")

        if not os.path.exists(model_path):
            raise Exception("repo_risk_model.pkl not found. Train repo model first.")

        self.model = joblib.load(model_path)

    def predict(self, repo_metrics: dict) -> float:

        feature_vector = self._build_feature_vector(repo_metrics)

        prediction = self.model.predict([feature_vector])[0]

        return float(np.clip(prediction, 0, 1))

    def _build_feature_vector(self, metrics: dict):

        return [
            metrics.get("avg_complexity", 0),
            metrics.get("avg_duplication", 0),
            metrics.get("test_coverage_ratio", 0),
            metrics.get("total_issues", 0) / max(metrics.get("total_files", 1), 1),
            metrics.get("security_issues", 0) / max(metrics.get("total_files", 1), 1),
        ]
