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
# SETTINGS
# ------------------------------------------------

MAX_LEN = 192
BATCH_SIZE = 12
EPOCHS = 3
MODEL_NAME = "microsoft/codebert-base"

# ------------------------------------------------
# PATHS
# ------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_FILE = os.path.join(BASE_DIR, "datasets", "mern_optimized.csv")

MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "mern_model.pt")

os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ------------------------------------------------
# DATASET
# ------------------------------------------------

class CodeDataset(Dataset):

    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):

        encoding = self.tokenizer(
            str(self.texts[idx]),
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )

        item = {k: v.squeeze(0) for k, v in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx])

        return item


# ------------------------------------------------
# TRAINING
# ------------------------------------------------

def train():

    print("CUDA Available:", torch.cuda.is_available())
    print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

    print("\nLoading dataset...")

    df = pd.read_csv(DATA_FILE)

    # Reduce dataset for faster training
    df = df.sample(40000, random_state=42)

    print("Dataset size:", len(df))
    print(df["label"].value_counts())

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df["code"].tolist(),
        df["label"].tolist(),
        test_size=0.1,
        stratify=df["label"],
        random_state=42
    )

    print("\nLoading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = CodeDataset(train_texts, train_labels, tokenizer, MAX_LEN)
    val_dataset = CodeDataset(val_texts, val_labels, tokenizer, MAX_LEN)

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        num_workers=0
    )

    print("\nLoading model...")

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2
    )

    model.to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=2e-5)

    scaler = torch.amp.GradScaler("cuda")

    # ------------------------------------------------
    # TRAIN LOOP
    # ------------------------------------------------

    for epoch in range(EPOCHS):

        print(f"\nEpoch {epoch+1}/{EPOCHS}")

        model.train()

        total_loss = 0

        progress = tqdm(train_loader)

        for batch in progress:

            batch = {k: v.to(DEVICE) for k, v in batch.items()}

            optimizer.zero_grad()

            with torch.amp.autocast("cuda"):

                outputs = model(**batch)

                loss = outputs.loss

            scaler.scale(loss).backward()

            scaler.step(optimizer)

            scaler.update()

            total_loss += loss.item()

            progress.set_postfix(loss=loss.item())

        print("Train Loss:", total_loss)

        # ------------------------------------------------
        # VALIDATION
        # ------------------------------------------------

        model.eval()

        preds = []
        labels = []

        with torch.no_grad():

            for batch in tqdm(val_loader):

                batch = {k: v.to(DEVICE) for k, v in batch.items()}

                outputs = model(**batch)

                logits = outputs.logits

                pred = torch.argmax(logits, dim=1)

                preds.extend(pred.cpu().numpy())
                labels.extend(batch["labels"].cpu().numpy())

        acc = accuracy_score(labels, preds)

        print("\nValidation Accuracy:", acc)

        torch.save(model.state_dict(), MODEL_PATH)

        print("Model saved →", MODEL_PATH)


# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__ == "__main__":
    train()