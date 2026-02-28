import os

from .file_static_analyzer import run_static_analysis
from .dependency_audit import analyze_dependencies
from .duplication_analysis import compute_duplication_ratio
from services.ml_engine.issue_model_inference import IssueModel


# Load model once (important)
issue_model = IssueModel()


EXCLUDED_DIRS = {
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}

MAX_FILE_SIZE = 500_000  # bytes


def analyze_repo(repo_path: str):
    """
    Analyze repository:
    - Detect tests
    - Compute duplication ratio & dependency risk
    - Run static analysis
    - Enrich issues using ML model
    """
    if not os.path.isdir(repo_path):
        raise ValueError(f"Not a directory: {repo_path}")

    results = []

    # ───────────────────────────────────────────────
    # Repo-wide metrics (computed once)
    # ───────────────────────────────────────────────
    has_tests = detect_tests(repo_path)
    dup_ratio = compute_duplication_ratio(repo_path)
    dep_score = analyze_dependencies(repo_path)

    for root, dirs, files in os.walk(repo_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for filename in files:
            if filename.endswith(".min.js"):
                continue

            if not filename.lower().endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                continue

            full_path = os.path.join(root, filename)

            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            # ───────────────────────────────────────────────
            # Static analysis
            # ───────────────────────────────────────────────
            static_result = run_static_analysis(full_path)

            static_result.setdefault("metrics", {})
            static_result.setdefault("issues", [])

            # Attach repo-wide metrics
            static_result["metrics"]["has_tests"] = 1 if has_tests else 0
            static_result["metrics"]["duplication_ratio"] = dup_ratio
            static_result["metrics"]["dependency_risk_score"] = dep_score

            static_result["file_path"] = os.path.relpath(full_path, repo_path)

            # ───────────────────────────────────────────────
            # 🔥 APPLY ISSUE ML MODEL HERE
            # ───────────────────────────────────────────────
            enriched_issues = []

            for issue in static_result["issues"]:
                try:
                    text_input = f"""
Issue Type: {issue.get("type", "")}
Severity: {issue.get("severity", "")}
Message: {issue.get("message", "")}
File Complexity: {static_result["metrics"].get("cyclomatic_complexity", 0)}
Duplication: {static_result["metrics"].get("duplication_ratio", 0)}
LOC: {static_result["metrics"].get("loc", 0)}
"""

                    prediction = issue_model.predict(text_input)

                    issue["ml_analysis"] = prediction

                except Exception as e:
                    issue["ml_analysis"] = {
                        "error": str(e)
                    }

                enriched_issues.append(issue)

            static_result["issues"] = enriched_issues

            results.append(static_result)

    return results


def detect_tests(repo_path: str) -> bool:
    test_indicators = {"test", "tests", "spec", "__tests__", "jest", "cypress"}

    for root, dirs, _ in os.walk(repo_path):
        for d in dirs:
            if any(ind in d.lower() for ind in test_indicators):
                return True

    return False