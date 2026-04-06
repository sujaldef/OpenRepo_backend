from sklearn.metrics import classification_report
from dataset_builder import build_dataset
import joblib


def evaluate(file_analyses):
    X, y = build_dataset(file_analyses)

    model = joblib.load("ml_training/saved_models/risk_model.pkl")

    preds = model.predict(X)

    print(classification_report(y, preds))