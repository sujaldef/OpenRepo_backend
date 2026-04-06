
import os
import pandas as pd
from datasets import load_dataset

BASE = os.path.dirname(os.path.dirname(__file__))
OUT = os.path.join(BASE, "datasets", "mern_dataset.csv")

data = []

# ------------------------------
# VALIDATION
# ------------------------------
def valid_code(code):
    if code is None:
        return False
    if len(code) < 50:
        return False
    if len(code) > 2000:
        return False
    return True


# ------------------------------
# DETECT WEB SECURITY PATTERNS
# ------------------------------
danger_patterns = [
    "eval(",
    "innerHTML",
    "document.write",
    "child_process",
    "exec(",
    "fs.writeFileSync",
    "req.body",
    "req.query",
    "dangerouslySetInnerHTML",
    "localStorage",
    "sessionStorage",
    "new Function(",
    "setTimeout(",
    "setInterval(",
    "SELECT * FROM",
    "password",
    "token",
]

def detect_issue(code):
    for p in danger_patterns:
        if p in code:
            return 1
    return 0


# ------------------------------
# LANGUAGES TO LOAD
# ------------------------------
languages = ["javascript", "python", "php", "java"]

for lang in languages:

    print(f"\nDownloading {lang} dataset...")

    ds = load_dataset("code_search_net", lang)

    for split in ["train", "validation", "test"]:

        for row in ds[split]:

            code = row["func_code_string"]

            if not valid_code(code):
                continue

            label = detect_issue(code)

            data.append({
                "code": code,
                "label": label
            })


# ------------------------------
# BUILD DATAFRAME
# ------------------------------
df = pd.DataFrame(data)

print("\nTotal samples before dedupe:", len(df))

df = df.drop_duplicates(subset=["code"])

print("Total samples after dedupe:", len(df))


# ------------------------------
# SAVE DATASET
# ------------------------------
df.to_csv(OUT, index=False)

print("\nMERN dataset saved to:", OUT)

print("\nLabel distribution:")
print(df["label"].value_counts())
