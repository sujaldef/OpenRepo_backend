# services/ml_engine/recommendation_engine.py

def generate_recommendations(file_results):

    recommendations = []

    for file in file_results:

        metrics = file.get("metrics", {})
        risk = file.get("risk_score", 0)

        # High Risk Overall
        if risk > 0.25:
            recommendations.append({
                "file_path": file["file_path"],
                "type": "High Risk",
                "priority": "High",
                "title": "File has elevated risk score",
                "description": "This file shows combined structural and issue-based risk signals.",
                "risk_score": risk
            })

        # Complexity
        if metrics.get("cyclomatic_complexity", 0) > 12:
            recommendations.append({
                "file_path": file["file_path"],
                "type": "Refactor",
                "priority": "Medium",
                "title": "Reduce Cyclomatic Complexity",
                "description": "Complex branching detected. Consider breaking into smaller functions."
            })

        # Security
        if metrics.get("security_issue_count", 0) > 0:
            recommendations.append({
                "file_path": file["file_path"],
                "type": "Security",
                "priority": "Critical",
                "title": "Security Issues Detected",
                "description": "File contains potential security vulnerabilities requiring review."
            })

        # No Tests
        if metrics.get("has_tests", 0) == 0 and risk > 0.15:
            recommendations.append({
                "file_path": file["file_path"],
                "type": "Testing",
                "priority": "Medium",
                "title": "Add Unit Tests",
                "description": "File has risk signals but lacks test coverage."
            })

        # Duplication
        if metrics.get("duplication_ratio", 0) > 0.3:
            recommendations.append({
                "file_path": file["file_path"],
                "type": "Maintainability",
                "priority": "Low",
                "title": "Reduce Code Duplication",
                "description": "Repeated patterns detected. Extract shared logic."
            })

    return recommendations