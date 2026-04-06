import os
import re
import pandas as pd
from transformers import AutoTokenizer

# ------------------------------------------------
# PATHS
# ------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INPUT_FILE = os.path.join(BASE_DIR, "datasets", "python_dataset.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "python_cleaned.csv")

MIN_CHARS = 50

# Chunking config
MAX_TOKENS = 512
STRIDE = 256

# ------------------------------------------------
# TOKENIZER (CodeBERT)
# ------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

# ------------------------------------------------
# CLEAN FUNCTION
# ------------------------------------------------
def clean_code(code: str):
    code = str(code)

    # Normalize tabs → spaces
    code = code.replace("\t", "    ")

    # Remove trailing spaces
    code = "\n".join([line.rstrip() for line in code.splitlines()])

    # Remove excessive blank lines
    code = re.sub(r"\n\s*\n+", "\n", code)

    # Strip edges
    code = code.strip()

    return code

# ------------------------------------------------
# SMART CHUNKING (FIXED VERSION)
# ------------------------------------------------
def chunk_code(code: str):
    tokens = tokenizer.encode(code, truncation=True, max_length=512)
    chunks = []

    for i in range(0, len(tokens), STRIDE):
        chunk_tokens = tokens[i:i + MAX_TOKENS]

        # Skip very small chunks
        if len(chunk_tokens) < 50:
            continue

        # Decode safely
        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

        # 🔒 HARD SAFETY CHECK
        encoded_len = len(tokenizer.encode(chunk_text, truncation=False))
        if encoded_len > MAX_TOKENS:
            chunk_tokens = chunk_tokens[:MAX_TOKENS]
            chunk_text = tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )

        chunks.append(chunk_text)

        if i + MAX_TOKENS >= len(tokens):
            break

    return chunks

# ------------------------------------------------
# MAIN CLEANING PIPELINE
# ------------------------------------------------
def clean_dataset():

    df = pd.read_csv(INPUT_FILE)

    print("Original size:", len(df))

    # Drop nulls
    df = df.dropna(subset=["code", "label"])

    # Remove duplicates (original level)
    df = df.drop_duplicates(subset=["code"])

    print("After dedup:", len(df))

    cleaned_codes = []
    cleaned_labels = []

    for code, label in zip(df["code"], df["label"]):

        code = clean_code(code)

        # Remove very small samples
        if len(code) < MIN_CHARS:
            continue

        # 🔥 SMART CHUNKING
        chunks = chunk_code(code)

        for chunk in chunks:
            cleaned_codes.append(chunk)
            cleaned_labels.append(label)

    clean_df = pd.DataFrame({
        "code": cleaned_codes,
        "label": cleaned_labels
    })

    # 🔥 REMOVE DUPLICATES AFTER CHUNKING
    clean_df = clean_df.drop_duplicates(subset=["code"])

    print("Final size:", len(clean_df))

    # Save
    clean_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✅ Clean dataset saved → {OUTPUT_FILE}")

# ------------------------------------------------
# DATASET ANALYSIS
# ------------------------------------------------
def analyze_dataset(file_path):

    print("\n==============================")
    print("DATASET QUALITY REPORT")
    print("==============================")

    df = pd.read_csv(file_path)

    print("\nTotal samples:", len(df))

    # NULL CHECK
    print("\nMissing values:\n", df.isnull().sum())

    # DUPLICATES
    duplicates = df.duplicated(subset=["code"]).sum()
    print("\nDuplicate samples:", duplicates)

    # LABEL DISTRIBUTION
    print("\nLabel distribution:")
    print(df["label"].value_counts())

    # CHAR LENGTH
    df["char_len"] = df["code"].apply(len)

    print("\nCode length stats (chars):")
    print("Min :", df["char_len"].min())
    print("Max :", df["char_len"].max())
    print("Mean:", int(df["char_len"].mean()))

    # TOKEN LENGTH
    def get_token_len(code):
     return len(tokenizer.encode(
        code,
        truncation=True,
        max_length=512
    ))

    print("\nCalculating token lengths (this may take time)...")
    df["token_len"] = df["code"].apply(get_token_len)

    print("\nToken length stats:")
    print("Min :", df["token_len"].min())
    print("Max :", df["token_len"].max())
    print("Mean:", int(df["token_len"].mean()))

    # TRUNCATION CHECK
    max_len = 512
    truncated = (df["token_len"] > max_len).sum()

    print(f"\nSamples exceeding {max_len} tokens:", truncated)
    print("Percentage:", round((truncated / len(df)) * 100, 2), "%")

    # SHORT CODE CHECK
    short_samples = (df["char_len"] < 50).sum()
    print("\nVery short samples (<50 chars):", short_samples)

    # CLASS BALANCE
    counts = df["label"].value_counts()
    ratio = counts.min() / counts.max()

    print("\nClass balance ratio:", round(ratio, 3))

    if ratio < 0.5:
        print("⚠️ Warning: Dataset is imbalanced")
    else:
        print("✅ Dataset is reasonably balanced")

    print("\n==============================\n")

# ------------------------------------------------
# RUN
# ------------------------------------------------
if __name__ == "__main__":
    clean_dataset()
    analyze_dataset(OUTPUT_FILE)