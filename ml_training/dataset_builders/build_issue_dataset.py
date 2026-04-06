import os
import pandas as pd
from sklearn.utils import shuffle

BASE = os.path.dirname(os.path.dirname(__file__))
DATA = os.path.join(BASE, "datasets")

files = [
    "python_dataset.csv",
    "clang_dataset.csv",
    "mern_dataset.csv"
]

dfs = []

for f in files:

    path = os.path.join(DATA, f)

    if os.path.exists(path):

        dfs.append(pd.read_csv(path))

df = pd.concat(dfs)

print("Total samples:", len(df))


# balance

vul = df[df.label == 1]
safe = df[df.label == 0]

min_n = min(len(vul), len(safe))

vul = vul.sample(min_n)
safe = safe.sample(min_n)

df = pd.concat([vul, safe])

df = shuffle(df)

df.to_csv(os.path.join(DATA, "issue_dataset.csv"), index=False)
print("Balanced dataset:", len(df))