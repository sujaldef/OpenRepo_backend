import hashlib
import os


def compute_duplication_ratio(repo_path: str):

    file_hashes = {}
    duplicate_count = 0
    total_files = 0

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                continue

            full_path = os.path.join(root, file)
            total_files += 1

            try:
                with open(full_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            except:
                continue

            if file_hash in file_hashes:
                duplicate_count += 1
            else:
                file_hashes[file_hash] = full_path

    if total_files == 0:
        return 0.0

    return duplicate_count / total_files