# Example path: services/ml_engine/risk_model.py

import os
import joblib
import numpy as np
import pandas as pd


class RiskModel:
    """
    Risk prediction model for individual files.
    Loads a pre-trained scikit-learn model and predicts multi-dimensional risk scores.
    """

    def __init__(self):
        # Resolve model path relative to this file
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../ml_training/saved_models")
        )
        model_path = os.path.join(base_dir, "risk_model.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Pre-trained model not found at: {model_path}\n"
                "Please train and save the model first."
            )

        self.model = joblib.load(model_path)
        self.feature_columns = [
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

        self.risk_keys = [
            "structural_risk",
            "security_risk",
            "maintainability_risk",
            "test_risk",
            "overall_risk"
        ]

    def predict(self, metrics: dict) -> dict:
        """
        Predict risk profile for a single file based on its metrics.

        Args:
            metrics: Dictionary containing code metrics

        Returns:
            Dictionary with risk scores (0.0–1.0) for different dimensions
        """
        feature_vector = self._build_feature_vector(metrics)

        # Create single-row DataFrame with correct column names
        df = pd.DataFrame([feature_vector], columns=self.feature_columns)

        # Model should return array of probabilities / scores
        prediction = self.model.predict(df)[0]

        # Clip values to valid [0, 1] range and round
        risk_profile = {
            key: round(float(np.clip(value, 0.0, 1.0)), 4)
            for key, value in zip(self.risk_keys, prediction)
        }

        return risk_profile

    def _build_feature_vector(self, metrics: dict) -> list:
        """
        Convert metrics dict to ordered list matching model training features.
        Uses safe .get() with sensible defaults.
        """
        return [
            metrics.get("loc", 0),
            metrics.get("function_count", 0),
            metrics.get("avg_function_length", 0),
            metrics.get("max_function_length", 0),
            metrics.get("cyclomatic_complexity", 1),       # default 1 (single path)
            metrics.get("max_nesting_depth", 0),
            metrics.get("total_issue_count", 0),
            metrics.get("security_issue_count", 0),
            metrics.get("duplication_ratio", 0.0),
            metrics.get("dependency_risk_score", 0.0),
            metrics.get("has_tests", 0),                    # 0 = no, 1 = yes
        ]


# Optional: small test / demo usage
if __name__ == "__main__":
    model = RiskModel()

    sample_metrics = {
        "loc": 120,
        "function_count": 4,
        "avg_function_length": 18,
        "max_function_length": 45,
        "cyclomatic_complexity": 7,
        "max_nesting_depth": 4,
        "total_issue_count": 3,
        "security_issue_count": 1,
        "duplication_ratio": 0.12,
        "dependency_risk_score": 0.45,
        "has_tests": 1
    }

    try:
        result = model.predict(sample_metrics)
        print("Risk Profile:")
        for k, v in result.items():
            print(f"  {k:22} : {v:.4f}")
    except Exception as e:
        print(f"Error during prediction: {e}")