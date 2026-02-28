# ml_training/train_risk_regressor.py

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "risk_model.pkl")

os.makedirs(os.path.join(BASE_DIR, "saved_models"), exist_ok=True)

df = pd.read_csv(DATASET_PATH)

X = df.drop(columns=[
    "structural_risk",
    "security_risk",
    "maintainability_risk",
    "test_risk",
    "overall_risk"
])

y = df[[
    "structural_risk",
    "security_risk",
    "maintainability_risk",
    "test_risk",
    "overall_risk"
]]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

joblib.dump(model, MODEL_PATH)

print("Multi-dimensional risk model saved.")