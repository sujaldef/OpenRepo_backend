import os
import joblib
import numpy as np


class StructureModel:

    def __init__(self):

        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../ml_training/saved_models")
        )

        path = os.path.join(base_dir, "folder_model.pkl")

        self.model = joblib.load(path) if os.path.exists(path) else None

    def is_available(self):
        return self.model is not None

    def predict(self, metrics: dict):

        if not self.model:
            return 0.0

        features = list(metrics.values())

        score = self.model.predict([features])[0]

        return float(np.clip(score, 0, 1))