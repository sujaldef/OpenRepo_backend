import os
import torch
import pandas as pd
from tqdm import tqdm

from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ------------------------------------------------
# SETTINGS
# ------------------------------------------------
MAX_LEN = 384
BATCH_SIZE = 8

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = os.path.dirname(__file__)

DATA_FILE = os.path.join(BASE_DIR, "datasets", "python_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

print("Using device:", DEVICE)

# ------------------------------------------------
# DATASET
# ------------------------------------------------
class CodeDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt"
        )

        item = {k: v.squeeze(0) for k, v in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx])

        return item

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
df = pd.read_csv(DATA_FILE)
df = df.dropna(subset=["code", "label"])

train_texts, test_texts, train_labels, test_labels = train_test_split(
    df["code"].tolist(),
    df["label"].tolist(),
    test_size=0.1,
    stratify=df["label"],
    random_state=42
)

# ------------------------------------------------
# LOAD MODEL (FIXED)
# ------------------------------------------------
print("\nLoading trained model...")

model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

model.to(DEVICE)
model.eval()

# ------------------------------------------------
# DATALOADER
# ------------------------------------------------
test_dataset = CodeDataset(test_texts, test_labels, tokenizer)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# ------------------------------------------------
# EVALUATION
# ------------------------------------------------
preds = []
labels = []

with torch.no_grad():
    for batch in tqdm(test_loader):
        batch = {k: v.to(DEVICE) for k, v in batch.items()}

        outputs = model(**batch)
        logits = outputs.logits

        probs = torch.softmax(logits, dim=1)[:, 1]
        pred = (probs > 0.4).long()   # threshold tuning

        preds.extend(pred.cpu().numpy())
        labels.extend(batch["labels"].cpu().numpy())

# ------------------------------------------------
# METRICS
# ------------------------------------------------
acc = accuracy_score(labels, preds)
precision = precision_score(labels, preds, zero_division=0)
recall = recall_score(labels, preds, zero_division=0)
f1 = f1_score(labels, preds, zero_division=0)
cm = confusion_matrix(labels, preds)

print("\n==============================")
print("FINAL MODEL EVALUATION")
print("==============================")

print("\nAccuracy :", round(acc, 4))
print("Precision:", round(precision, 4))
print("Recall   :", round(recall, 4))
print("F1 Score :", round(f1, 4))

print("\nConfusion Matrix")
print(cm)

print("\nPrediction Distribution:")
print(pd.Series(preds).value_counts())