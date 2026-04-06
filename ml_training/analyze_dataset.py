import os
import pandas as pd
import hashlib

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "datasets")

files = [
    "python_dataset.csv",
    "clang_cleaned.csv",
    "mern_optimized.csv"
]


def hash_code(code):
    return hashlib.md5(code.encode()).hexdigest()


for file in files:

    path = os.path.join(DATA, file)

    if not os.path.exists(path):
        print(f"{file} not found\n")
        continue

    print("\n==============================")
    print(f"DATASET: {file}")
    print("==============================")

    df = pd.read_csv(path)

    print("Total rows:", len(df))

    # unique code samples
    unique_codes = df["code"].nunique()
    print("Unique code samples:", unique_codes)

    duplicates = len(df) - unique_codes
    print("Duplicate samples:", duplicates)

    # label distribution
    if "label" in df.columns:
        print("\nLabel distribution:")
        print(df["label"].value_counts())

    # code length statistics
    df["code_len"] = df["code"].astype(str).apply(len)

    print("\nCode length stats:")
    print("Min:", df["code_len"].min())
    print("Max:", df["code_len"].max())
    print("Mean:", int(df["code_len"].mean()))

    # detect identical code with different labels
    if "label" in df.columns:

        df["hash"] = df["code"].apply(hash_code)

        conflict = df.groupby("hash")["label"].nunique()
        conflicts = conflict[conflict > 1]

        print("\nConflicting labels:", len(conflicts))

    print("\n")