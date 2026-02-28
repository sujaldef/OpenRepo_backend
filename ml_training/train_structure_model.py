import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


def train_structure_model():

    df = pd.read_csv("ml_training/structure_dataset.csv")

    if len(df) < 5:
        print("Not enough data.")
        return

    X = df.drop(columns=["structure_risk"])
    y = df["structure_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    os.makedirs("ml_training/saved_models", exist_ok=True)
    joblib.dump(model, "ml_training/saved_models/folder_model.pkl")

    print("Structure model trained.")


if __name__ == "__main__":
    train_structure_model()