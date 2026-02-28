import os
import pandas as pd
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from torch.nn import CrossEntropyLoss
from tqdm import tqdm

# ------------------------------------------------
# GPU INFO
# ------------------------------------------------
print("CUDA Available:", torch.cuda.is_available())
print("CUDA Count:", torch.cuda.device_count())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")

# ------------------------------------------------
# PATHS
# ------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "issue_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "issue_model.pt")

os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

# ------------------------------------------------
# DATASET CLASS
# ------------------------------------------------
class IssueDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )

        item = {key: val.squeeze(0) for key, val in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


# ------------------------------------------------
# TRAIN FUNCTION
# ------------------------------------------------
def train():

    df = pd.read_csv(DATA_FILE)

    # Remove NaNs
    df = df.dropna(subset=["code", "label"])

    print("\nClass Distribution:")
    print(df["label"].value_counts())

    # ------------------------------------------------
    # STRATIFIED SPLIT (IMPORTANT)
    # ------------------------------------------------
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["code"],
        df["label"],
        test_size=0.1,
        random_state=42,
        stratify=df["label"]
    )

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base", use_fast=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        "microsoft/codebert-base",
        num_labels=2
    )

    # ------------------------------------------------
    # LOAD EXISTING MODEL IF PRESENT
    # ------------------------------------------------
    if os.path.exists(MODEL_SAVE_PATH):
        print("Loading existing model...")
        model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=DEVICE))
        print("Model loaded successfully.")

    model.to(DEVICE)

    train_dataset = IssueDataset(train_texts.tolist(), train_labels.tolist(), tokenizer)
    val_dataset = IssueDataset(val_texts.tolist(), val_labels.tolist(), tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)

    # ------------------------------------------------
    # CLASS WEIGHTING (CRITICAL IF IMBALANCED)
    # ------------------------------------------------
    class_counts = df["label"].value_counts().sort_index().values
    weights = 1.0 / class_counts
    weights = weights / weights.sum()
    class_weights = torch.tensor(weights, dtype=torch.float).to(DEVICE)

    loss_fn = CrossEntropyLoss(weight=class_weights)

    optimizer = AdamW(model.parameters(), lr=1e-5)

    # ------------------------------------------------
    # MULTI-EPOCH TRAINING
    # ------------------------------------------------
    epochs = 2

    for epoch in range(epochs):
        print(f"\n===== EPOCH {epoch+1}/{epochs} =====")

        model.train()
        total_loss = 0

        for batch in tqdm(train_loader):
            batch = {k: v.to(DEVICE) for k, v in batch.items()}

            outputs = model(**batch)
            logits = outputs.logits

            loss = loss_fn(logits, batch["labels"])

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Training Loss: {total_loss:.4f}")

        # ------------------------------------------------
        # VALIDATION
        # ------------------------------------------------
        model.eval()
        predictions = []
        true_labels = []

        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(DEVICE) for k, v in batch.items()}
                outputs = model(**batch)
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1)

                predictions.extend(preds.cpu().numpy())
                true_labels.extend(batch["labels"].cpu().numpy())

        acc = accuracy_score(true_labels, predictions)
        print("Validation Accuracy:", acc)
        print("\nClassification Report:")
        print(classification_report(true_labels, predictions))

        # ------------------------------------------------
        # SAVE MODEL AFTER EACH EPOCH
        # ------------------------------------------------
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        print("Model saved.")

    print("\nTraining complete.")


if __name__ == "__main__":
    train()