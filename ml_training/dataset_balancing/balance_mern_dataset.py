import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "mern_dataset.csv"))
print("Original distribution:")
print(df["label"].value_counts())

vul = df[df.label == 1]
safe = df[df.label == 0]

safe_sample = safe.sample(len(vul), random_state=42)

balanced = pd.concat([vul, safe_sample])

balanced = balanced.sample(frac=1, random_state=42)
balanced.to_csv(os.path.join(BASE_DIR, "datasets", "mern_balanced.csv"), index=False)
print("\nBalanced distribution:")
print(balanced["label"].value_counts())

print("\nFinal dataset size:", len(balanced))