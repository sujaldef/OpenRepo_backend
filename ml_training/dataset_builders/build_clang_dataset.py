import os
import json
import pandas as pd

BASE = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(BASE, "raw_datasets")
OUT = os.path.join(BASE, "datasets", "clang_dataset.csv")

data = []

def valid_code(code):
    if code is None:
        return False
    if len(code) < 50:
        return False
    if len(code) > 2000:
        return False
    return True


# Devign
devign = os.path.join(RAW, "devign", "dataset.json")

with open(devign) as f:

    items = json.load(f)

    for obj in items:

        code = obj["func"]

        if not valid_code(code):
            continue

        data.append({
            "code": code,
            "label": int(obj["target"])
        })


# BigVul
for split in ["trainBIGVUL.parquet", "validationBIGVUL.parquet", "testBIGVUL.parquet"]:

    path = os.path.join(RAW, "BigVul", split)

    if not os.path.exists(path):
        continue

    df = pd.read_parquet(path)

    for _, row in df.iterrows():

        code = row["func_before"]

        if not valid_code(code):
            continue

        data.append({
            "code": code,
            "label": int(row["vul"])
        })


df = pd.DataFrame(data)

df = df.drop_duplicates(subset=["code"])

df.to_csv(OUT, index=False)

print("C dataset:", len(df))