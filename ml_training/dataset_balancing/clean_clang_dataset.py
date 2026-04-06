import os
import re
import pandas as pd

# ---------------------------------------------------
# PATHS
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INPUT_FILE = os.path.join(BASE_DIR, "datasets", "clang_balanced.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "clang_cleaned.csv")

print("Loading dataset:", INPUT_FILE)

df = pd.read_csv(INPUT_FILE)

print("Original size:", len(df))


# ---------------------------------------------------
# CLEAN FUNCTIONS
# ---------------------------------------------------

def remove_comments(code):

    # remove /* */ comments
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)

    # remove // comments
    code = re.sub(r"//.*", "", code)

    return code


def remove_preprocessor(code):

    lines = code.split("\n")

    cleaned = []

    for line in lines:
        if not line.strip().startswith("#"):
            cleaned.append(line)

    return "\n".join(cleaned)


def normalize_whitespace(code):

    code = re.sub(r"\s+", " ", code)

    return code.strip()


# ---------------------------------------------------
# APPLY CLEANING
# ---------------------------------------------------

clean_codes = []

for code in df["code"]:

    code = str(code)

    code = remove_comments(code)

    code = remove_preprocessor(code)

    code = normalize_whitespace(code)

    clean_codes.append(code)


df["code"] = clean_codes


# ---------------------------------------------------
# REMOVE SHORT SAMPLES
# ---------------------------------------------------

df["len"] = df["code"].apply(len)

df = df[df["len"] > 80]

print("After removing small samples:", len(df))


# ---------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------

df = df.drop_duplicates(subset=["code"])

print("After removing duplicates:", len(df))


# ---------------------------------------------------
# TRIM VERY LONG CODE
# ---------------------------------------------------

MAX_CHARS = 2000

df["code"] = df["code"].apply(lambda x: x[:MAX_CHARS])


# ---------------------------------------------------
# FINAL DATASET
# ---------------------------------------------------

df = df[["code", "label"]]

df.to_csv(OUTPUT_FILE, index=False)

print("Clean dataset saved to:", OUTPUT_FILE)

print("Final dataset size:", len(df))
print(df["label"].value_counts())