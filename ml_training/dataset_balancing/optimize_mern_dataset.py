import os
import pandas as pd
import re
from transformers import AutoTokenizer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INPUT_FILE = os.path.join(BASE_DIR, "datasets", "mern_balanced.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "mern_optimized.csv")

print("Loading dataset...")
df = pd.read_csv(INPUT_FILE)

print("Original size:", len(df))


# ------------------------------------------------
# Remove extreme long samples
# ------------------------------------------------

df["length"] = df["code"].apply(len)

df = df[df["length"] < 1500]

print("After removing long samples:", len(df))


# ------------------------------------------------
# Clean whitespace
# ------------------------------------------------

def clean_code(code):

    code = str(code)

    code = re.sub(r"\s+", " ", code)

    return code.strip()


df["code"] = df["code"].apply(clean_code)


# ------------------------------------------------
# Token limit check
# ------------------------------------------------

print("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")


def truncate_tokens(code):

    tokens = tokenizer.tokenize(code)

    if len(tokens) > 256:
        tokens = tokens[:256]

    return tokenizer.convert_tokens_to_string(tokens)


df["code"] = df["code"].apply(truncate_tokens)


# ------------------------------------------------
# Balance dataset
# ------------------------------------------------

print("Balancing dataset...")

label0 = df[df["label"] == 0]
label1 = df[df["label"] == 1]

min_size = min(len(label0), len(label1))

target_size = min(min_size, 30000)

label0 = label0.sample(target_size, random_state=42)
label1 = label1.sample(target_size, random_state=42)

df_balanced = pd.concat([label0, label1]).sample(frac=1, random_state=42)


print("Final dataset size:", len(df_balanced))
print(df_balanced["label"].value_counts())


# ------------------------------------------------
# Save dataset
# ------------------------------------------------

df_balanced = df_balanced[["code", "label"]]

df_balanced.to_csv(OUTPUT_FILE, index=False)

print("Optimized dataset saved to:")
print(OUTPUT_FILE)