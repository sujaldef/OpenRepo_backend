
import os
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
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

    def __init__(self, texts, labels, tokenizer, max_length=384):
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

    print("Dataset size:", len(df))

    # stratified split
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["code"].tolist(),
        df["label"].tolist(),
        test_size=0.1,
        stratify=df["label"],
        random_state=42
    )

    tokenizer = AutoTokenizer.from_pretrained(
        "microsoft/codebert-base",
        use_fast=True
    )

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

    train_dataset = IssueDataset(train_texts, train_labels, tokenizer)
    val_dataset = IssueDataset(val_texts, val_labels, tokenizer)

    train_loader = DataLoader(
        train_dataset,
        batch_size=8,
        shuffle=True,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=8,
        pin_memory=True
    )

    optimizer = AdamW(model.parameters(), lr=2e-5)

    scaler = torch.cuda.amp.GradScaler()

    epochs = 3

    # ------------------------------------------------
    # TRAIN LOOP
    # ------------------------------------------------
    for epoch in range(epochs):

        print(f"\nEpoch {epoch+1}/{epochs}")

        model.train()
        total_loss = 0

        for batch in tqdm(train_loader):

            batch = {k: v.to(DEVICE) for k, v in batch.items()}

            optimizer.zero_grad()

            with torch.cuda.amp.autocast():

                outputs = model(**batch)
                loss = outputs.loss

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()

        print("Training Loss:", total_loss)

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

        # save checkpoint
        torch.save(model.state_dict(), MODEL_SAVE_PATH)

        print("Model saved")

    print("\nTraining complete")


# ------------------------------------------------
# RUN
# ------------------------------------------------
if __name__ == "__main__":
    train()

