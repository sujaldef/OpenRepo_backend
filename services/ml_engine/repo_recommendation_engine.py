# services/ml_engine/repo_recommendation_engine.py

def generate_repo_recommendations(repo_metrics):

    if not repo_metrics:
        return []

    recommendations = []

    avg_risk = repo_metrics.get("avg_risk", 0)
    avg_complexity = repo_metrics.get("avg_complexity", 0)
    total_issues = repo_metrics.get("total_issues", 0)
    security_issues = repo_metrics.get("security_issues", 0)
    avg_duplication = repo_metrics.get("avg_duplication", 0)
    test_ratio = repo_metrics.get("test_coverage_ratio", 1)
    total_files = repo_metrics.get("total_files", 1)

    # -----------------------------
    # Derived Density Signals
    # -----------------------------

    issue_density = total_issues / max(total_files, 1)

    pressure_score = (
        (avg_risk * 2) +
        (avg_complexity / 10) +
        issue_density +
        avg_duplication +
        (1 - test_ratio)
    )

    # -----------------------------
    # 1️⃣ Structural Risk
    # -----------------------------
    if avg_risk > 0.12:
        severity = score_to_priority(avg_risk * 3)

        recommendations.append({
            "type": "Architecture",
            "priority": severity,
            "score": round(avg_risk, 3),
            "title": "Elevated Structural Risk",
            "description": (
                "The repository shows above-average structural fragility. "
                "Refactoring high-risk modules could prevent future maintenance overhead."
            )
        })

    # -----------------------------
    # 2️⃣ Complexity Load
    # -----------------------------
    if avg_complexity > 6:
        severity = score_to_priority(avg_complexity / 15)

        recommendations.append({
            "type": "Refactor",
            "priority": severity,
            "score": round(avg_complexity, 2),
            "title": "High Complexity Density",
            "description": (
                "Branch-heavy logic appears across modules. "
                "Consider modular decomposition and smaller function boundaries."
            )
        })

    # -----------------------------
    # 3️⃣ Technical Debt
    # -----------------------------
    if issue_density > 0.3:
        severity = score_to_priority(issue_density)

        recommendations.append({
            "type": "Maintainability",
            "priority": severity,
            "score": round(issue_density, 3),
            "title": "Accumulated Technical Debt",
            "description": (
                "Static analysis warnings are frequent across files. "
                "Address recurring smells before they compound."
            )
        })

    # -----------------------------
    # 4️⃣ Duplication Pressure
    # -----------------------------
    if avg_duplication > 0.2:
        severity = score_to_priority(avg_duplication)

        recommendations.append({
            "type": "Maintainability",
            "priority": severity,
            "score": round(avg_duplication, 3),
            "title": "Code Duplication Pressure",
            "description": (
                "Shared patterns are repeated across modules. "
                "Extract reusable components to reduce maintenance cost."
            )
        })

    # -----------------------------
    # 5️⃣ Test Weakness
    # -----------------------------
    if test_ratio < 0.6:
        severity = score_to_priority(1 - test_ratio)

        recommendations.append({
            "type": "Testing",
            "priority": severity,
            "score": round(1 - test_ratio, 3),
            "title": "Insufficient Test Coverage",
            "description": (
                "A significant portion of the repository lacks test coverage. "
                "Introduce unit and integration tests for high-risk modules."
            )
        })

    # -----------------------------
    # 6️⃣ Security
    # -----------------------------
    if security_issues > 0:
        recommendations.append({
            "type": "Security",
            "priority": "Critical",
            "score": security_issues,
            "title": "Security Vulnerabilities Detected",
            "description": (
                "Security-related issues were found. "
                "Immediate review is recommended."
            )
        })

    # -----------------------------
    # Rank by computed pressure
    # -----------------------------
    recommendations = sorted(
        recommendations,
        key=lambda x: priority_weight(x["priority"]),
        reverse=True
    )

    return recommendations


# ---------------------------------------------------
# PRIORITY SCORING
# ---------------------------------------------------

def score_to_priority(score):

    if score > 0.7:
        return "High"
    elif score > 0.4:
        return "Medium"
    else:
        return "Low"


def priority_weight(priority):

    weights = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    return weights.get(priority, 0)