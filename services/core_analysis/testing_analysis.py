import os


def analyze_testing(repo_path: str):

    issues = []

    has_tests = any("test" in d.lower() for d in os.listdir(repo_path))

    if not has_tests:
        issues.append({
            "type": "Testing",
            "severity": "warning",
            "message": "No tests detected in project"
        })

    return {"issues": issues}