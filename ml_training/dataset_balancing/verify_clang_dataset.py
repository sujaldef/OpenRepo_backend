import os
import pandas as pd
import random

# ------------------------------------------------
# PATH
# ------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_FILE = os.path.join(BASE_DIR, "datasets", "mern_balanced.csv")

print("\nLoading dataset:", DATA_FILE)

df = pd.read_csv(DATA_FILE)

# ------------------------------------------------
# 1. BASIC INFO
# ------------------------------------------------

print("\n==============================")
print("1. DATASET SHAPE")
print("==============================")

print("Total rows:", len(df))
print("Columns:", df.columns.tolist())


# ------------------------------------------------
# 2. LABEL DISTRIBUTION
# ------------------------------------------------

print("\n==============================")
print("2. LABEL DISTRIBUTION")
print("==============================")

print(df["label"].value_counts())


# ------------------------------------------------
# 3. CODE LENGTH STATS
# ------------------------------------------------

df["length"] = df["code"].apply(len)

print("\n==============================")
print("3. CODE LENGTH STATS")
print("==============================")

print("Min:", df["length"].min())
print("Max:", df["length"].max())
print("Mean:", int(df["length"].mean()))


# ------------------------------------------------
# 4. EMPTY CODE CHECK
# ------------------------------------------------

print("\n==============================")
print("4. EMPTY CODE CHECK")
print("==============================")

empty = df[df["code"].str.strip() == ""]
print("Empty samples:", len(empty))


# ------------------------------------------------
# 5. DUPLICATE CHECK
# ------------------------------------------------

print("\n==============================")
print("5. DUPLICATE CHECK")
print("==============================")

duplicates = df.duplicated(subset=["code"]).sum()
print("Duplicate code samples:", duplicates)


# ------------------------------------------------
# 6. MACRO CHECK
# ------------------------------------------------

print("\n==============================")
print("6. MACRO CHECK")
print("==============================")

macro_samples = df[df["code"].str.contains("#include|#define|#ifdef", regex=True)]

print("Samples still containing macros:", len(macro_samples))


# ------------------------------------------------
# 7. COMMENT CHECK
# ------------------------------------------------

print("\n==============================")
print("7. COMMENT CHECK")
print("==============================")

comment_samples = df[df["code"].str.contains("//|/\*", regex=True)]

print("Samples still containing comments:", len(comment_samples))


# ------------------------------------------------
# 8. TRUNCATION CHECK
# ------------------------------------------------

print("\n==============================")
print("8. TRUNCATION CHECK")
print("==============================")

long_samples = df[df["length"] >= 2000]

print("Samples near truncation limit:", len(long_samples))


# ------------------------------------------------
# 9. RANDOM SAMPLE PREVIEW
# ------------------------------------------------

print("\n==============================")
print("9. RANDOM CODE SAMPLES")
print("==============================")

samples = df.sample(5)

for i, row in samples.iterrows():

    print("\n----- SAMPLE -----")
    print("Label:", row["label"])
    print("Code snippet:\n")
    print(row["code"][:400])


# ------------------------------------------------
# 10. UNIQUE SAMPLE CHECK
# ------------------------------------------------

print("\n==============================")
print("10. UNIQUE CODE CHECK")
print("==============================")

unique_count = df["code"].nunique()

print("Unique samples:", unique_count)
print("Duplicate ratio:", round((1 - unique_count / len(df)) * 100, 2), "%")


print("\n✔ DATASET VERIFICATION COMPLETE")