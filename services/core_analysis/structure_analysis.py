import os

# Checks:

# Missing README

# Missing tests folder

# Flat structure
def analyze_structure(repo_path: str):

    issues = []

    if not os.path.exists(os.path.join(repo_path, "README.md")):
        issues.append({
            "type": "Documentation",
            "severity": "warning",
            "message": "README.md is missing"
        })

    if not any("test" in d.lower() for d in os.listdir(repo_path)):
        issues.append({
            "type": "Testing",
            "severity": "warning",
            "message": "No test folder detected"
        })

    if len(os.listdir(repo_path)) > 20:
        issues.append({
            "type": "Structure",
            "severity": "info",
            "message": "Project root contains too many files"
        })

    return {"issues": issues}