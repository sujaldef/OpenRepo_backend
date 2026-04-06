import os
import pandas as pd
from transformers import AutoTokenizer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "datasets", "mern_balanced.csv")

print("\nLoading dataset:", DATA_FILE)

df = pd.read_csv(DATA_FILE)

print("\n==============================")
print("DATASET SHAPE")
print("==============================")

print("Rows:", len(df))
print("Columns:", df.columns.tolist())

print("\n==============================")
print("LABEL DISTRIBUTION")
print("==============================")

print(df["label"].value_counts())

print("\n==============================")
print("DUPLICATES")
print("==============================")

duplicates = df.duplicated(subset=["code"]).sum()
print("Duplicate samples:", duplicates)

print("\n==============================")
print("CODE LENGTH STATS")
print("==============================")

df["length"] = df["code"].apply(len)

print("Min:", df["length"].min())
print("Max:", df["length"].max())
print("Mean:", int(df["length"].mean()))

print("\n==============================")
print("TOKEN LENGTH STATS")
print("==============================")

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

token_lengths = df["code"].apply(lambda x: len(tokenizer.tokenize(str(x))))

print("Min tokens:", token_lengths.min())
print("Max tokens:", token_lengths.max())
print("Avg tokens:", int(token_lengths.mean()))