# ml_training/train_repo_model.py

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


def train_repo_model():

    base_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(base_dir, "repo_dataset.csv")

    df = pd.read_csv(dataset_path)

    X = df.drop("avg_risk", axis=1)
    y = df["avg_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mse = mean_squared_error(y_test, preds)

    print("Repo Model MSE:", mse)

    save_dir = os.path.join(base_dir, "saved_models")
    os.makedirs(save_dir, exist_ok=True)

    model_path = os.path.join(save_dir, "repo_risk_model.pkl")

    joblib.dump(model, model_path)

    print("Repo model saved to:", model_path)


if __name__ == "__main__":
    train_repo_model()