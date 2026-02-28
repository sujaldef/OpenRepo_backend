import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
RAW_DIR = os.path.join(BASE_DIR, "raw_datasets")
OUTPUT_FILE = os.path.join(BASE_DIR, "issue_dataset.csv")


# ---------------------------------------------------
# Load CodeXGLUE (Python Only)
# ---------------------------------------------------
def load_codexglue():
    data = []

    for split in ["train.parquet", "validation.parquet", "test.parquet"]:
        path = os.path.join(RAW_DIR, "codexglue", split)

        if not os.path.exists(path):
            continue

        df = pd.read_parquet(path)

        for _, row in df.iterrows():
            code = str(row["func"]).strip()
            label = int(row["target"])

            data.append({
                "code": code,
                "label": label,
                "language": "python"
            })

    return data


# ---------------------------------------------------
# Cleaning
# ---------------------------------------------------
def clean_dataset(df):

    # Remove null / empty
    df = df.dropna(subset=["code"])
    df = df[df["code"].str.strip() != ""]

    # Remove extremely short snippets (< 5 lines)
    df = df[df["code"].str.count("\n") >= 5]

    # Remove extremely long functions (> 500 lines)
    df = df[df["code"].str.count("\n") <= 500]

    # Remove duplicates
    df = df.drop_duplicates(subset=["code"])

    df = df.reset_index(drop=True)

    return df


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
def main():

    print("Loading CodeXGLUE (Python only)...")
    codex_data = load_codexglue()

    df = pd.DataFrame(codex_data)

    print("Total raw samples:", len(df))

    df = clean_dataset(df)

    print("After cleaning:", len(df))

    print("\nLabel distribution:")
    print(df["label"].value_counts())

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved cleaned dataset to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()