import os
import json


def analyze_dependencies(repo_path: str):

    score = 0.0

    package_json = os.path.join(repo_path, "package.json")

    if os.path.exists(package_json):
        try:
            with open(package_json, "r") as f:
                data = json.load(f)

            deps = data.get("dependencies", {})
            dep_count = len(deps)

            score = min(dep_count / 100, 1.0)
        except:
            pass

    return score