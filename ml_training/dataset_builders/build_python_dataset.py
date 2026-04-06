import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(BASE, "raw_datasets")
OUT = os.path.join(BASE, "datasets", "python_dataset.csv")

data = []

def valid_code(code):
    if code is None:
        return False
    if len(code) < 50:
        return False
    if len(code) > 2000:
        return False
    return True


# CodeXGLUE
for split in ["train.parquet", "validation.parquet", "test.parquet"]:

    path = os.path.join(RAW, "codexglue", split)

    if not os.path.exists(path):
        continue

    df = pd.read_parquet(path)

    for _, row in df.iterrows():

        code = row["func"]

        if not valid_code(code):
            continue

        data.append({
            "code": code,
            "label": int(row["target"])
        })


# CodeSearchNet Python (safe code)
csn = os.path.join(RAW, "CodeSearchNet", "python")

if os.path.exists(csn):

    for file in os.listdir(csn):

        if file.endswith(".jsonl"):

            df = pd.read_json(os.path.join(csn, file), lines=True)

            for _, row in df.iterrows():

                code = row["func_code_string"]

                if not valid_code(code):
                    continue

                data.append({
                    "code": code,
                    "label": 0
                })


df = pd.DataFrame(data)

df = df.drop_duplicates(subset=["code"])

df.to_csv(OUT, index=False)

print("Python dataset:", len(df))