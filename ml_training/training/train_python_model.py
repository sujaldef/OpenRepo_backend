import os
import re
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup
)
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
from tqdm import tqdm

# ------------------------------------------------
# PATHS
# ------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ✅ FIXED: use CLEAN dataset
DATA_FILE = os.path.join(BASE_DIR, "datasets", "python_cleaned.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

# ------------------------------------------------
# CLEAN CODE
# ------------------------------------------------
def clean_code(code: str):
    code = str(code)
    code = code.replace("\t", "    ")
    code = re.sub(r"\n\s*\n+", "\n", code)
    code = "\n".join([line.rstrip() for line in code.splitlines()])
    return code.strip()

# ------------------------------------------------
# DATASET
# ------------------------------------------------
class CodeDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=512):
        self.texts = [clean_code(t) for t in texts]
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )

        item = {k: v.squeeze(0) for k, v in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

# ------------------------------------------------
# TRAIN
# ------------------------------------------------
def train():

    df = pd.read_csv(DATA_FILE)

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["code"].tolist(),
        df["label"].tolist(),
        test_size=0.1,
        stratify=df["label"],
        random_state=42
    )

    # Class weights
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(train_labels),
        y=train_labels
    )
    class_weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

    model = AutoModelForSequenceClassification.from_pretrained(
        "microsoft/codebert-base",
        num_labels=2
    )

    model.to(DEVICE)

    train_dataset = CodeDataset(train_texts, train_labels, tokenizer)
    val_dataset = CodeDataset(val_texts, val_labels, tokenizer)

    # ✅ Increased batch size (adjust if GPU limited)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)

    optimizer = AdamW(model.parameters(), lr=2e-5)

    # ✅ Scheduler added
    epochs = 3
    total_steps = len(train_loader) * epochs

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )

    loss_fn = nn.CrossEntropyLoss(weight=class_weights)

    best_acc = 0

    for epoch in range(epochs):

        print(f"\nEpoch {epoch+1}/{epochs}")

        model.train()
        total_loss = 0

        for batch in tqdm(train_loader):
            batch = {k: v.to(DEVICE) for k, v in batch.items()}

            optimizer.zero_grad()

            outputs = model(**batch)
            loss = loss_fn(outputs.logits, batch["labels"])

            loss.backward()

            # ✅ Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            optimizer.step()
            scheduler.step()

            total_loss += loss.item()

        print("Train Loss:", round(total_loss, 4))

        # ------------------------------------------------
        # VALIDATION
        # ------------------------------------------------
        model.eval()
        preds, labels = [], []

        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(DEVICE) for k, v in batch.items()}

                outputs = model(**batch)
                pred = torch.argmax(outputs.logits, dim=1)

                preds.extend(pred.cpu().numpy())
                labels.extend(batch["labels"].cpu().numpy())

        acc = accuracy_score(labels, preds)
        print("Validation Accuracy:", acc)

        print("\nClassification Report:")
        print(classification_report(labels, preds))

        # Save best model
        if acc > best_acc:
            best_acc = acc
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print("✅ Best model saved")

    print("\n🔥 Training complete. Best Accuracy:", best_acc)


# ------------------------------------------------
# RUN
# ------------------------------------------------
if __name__ == "__main__":
    train()