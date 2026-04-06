import os
from services.core_analysis.file_static_analyzer import run_static_analysis


EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next"
}

MAX_FILE_SIZE = 500_000


def analyze_repo(repo_path: str):

    results = []

    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:

            if file.endswith(".min.js"):
                continue

            if not file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                continue

            full_path = os.path.join(root, file)

            if os.path.getsize(full_path) > MAX_FILE_SIZE:
                continue

            static_result = run_static_analysis(full_path)

            results.append(static_result)

    return results