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

DATA_FILE = os.path.join(BASE_DIR, "datasets", "clang_cleaned.csv")

MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "c_model.pt")

os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Using device:", DEVICE)

# ------------------------------------------------
# DATASET
# ------------------------------------------------
class CodeDataset(Dataset):

    def __init__(self, texts, labels, tokenizer, max_len=384):
        self.texts = texts
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
        item["labels"] = torch.tensor(self.labels[idx])

        return item


# ------------------------------------------------
# TRAIN
# ------------------------------------------------
def train():

    df = pd.read_csv(DATA_FILE)

    print("Dataset size:", len(df))
    print(df["label"].value_counts())

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["code"].tolist(),
        df["label"].tolist(),
        test_size=0.1,
        stratify=df["label"],
        random_state=42
    )

    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

    model = AutoModelForSequenceClassification.from_pretrained(
        "microsoft/codebert-base",
        num_labels=2
    )

    model.to(DEVICE)

    train_dataset = CodeDataset(train_texts, train_labels, tokenizer)
    val_dataset = CodeDataset(val_texts, val_labels, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=8)

    optimizer = AdamW(model.parameters(), lr=2e-5)

    epochs = 3

    for epoch in range(epochs):

        print(f"\nEpoch {epoch+1}/{epochs}")

        model.train()
        total_loss = 0

        for batch in tqdm(train_loader):

            batch = {k: v.to(DEVICE) for k, v in batch.items()}

            optimizer.zero_grad()

            outputs = model(**batch)

            loss = outputs.loss

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

        print("Train Loss:", total_loss)

        # VALIDATION

        model.eval()

        preds = []
        labels = []

        with torch.no_grad():

            for batch in val_loader:

                batch = {k: v.to(DEVICE) for k, v in batch.items()}

                outputs = model(**batch)

                logits = outputs.logits

                pred = torch.argmax(logits, dim=1)

                preds.extend(pred.cpu().numpy())
                labels.extend(batch["labels"].cpu().numpy())

        acc = accuracy_score(labels, preds)

        print("Validation Accuracy:", acc)

        torch.save(model.state_dict(), MODEL_PATH)

        print("Model saved →", MODEL_PATH)


if __name__ == "__main__":
    train()