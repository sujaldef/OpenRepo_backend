# services/ml_engine/repo_insight_engine.py

from collections import defaultdict


def build_repo_insight_summary(file_results, repo_metrics, structure_metrics):

    total_files = len(file_results)

    # Top risky files
    top_risky_files = sorted(
        file_results,
        key=lambda x: x.get("risk_score", 0),
        reverse=True
    )[:5]

    # 🔥 FIX: Return FULL file objects (with risk_score, complexity, etc), not just paths
    # The LLM engines need file.get('risk_score') to work!
    top_risky_files_with_metadata = []
    for f in top_risky_files:
        top_risky_files_with_metadata.append({
            "file_path": f.get("file_path"),
            "folder_path": f.get("folder_path"),
            "risk_score": f.get("risk_score", 0),
            "complexity": f.get("metrics", {}).get("cyclomatic_complexity", 0),
            "security_issues": f.get("metrics", {}).get("security_issue_count", 0)
        })

    # Security hotspots
    security_hotspots = [
        f["file_path"]
        for f in file_results
        if f.get("metrics", {}).get("security_issue_count", 0) > 0
    ]

    # Risk concentration ratio
    total_risk = sum(f.get("risk_score", 0) for f in file_results)
    top_risk_sum = sum(f.get("risk_score", 0) for f in top_risky_files)

    risk_concentration_ratio = round(
        top_risk_sum / total_risk, 4
    ) if total_risk > 0 else 0

    return {
        "repo_metrics": repo_metrics,
        "structure_metrics": structure_metrics,
        "top_risky_files": top_risky_files_with_metadata,
        "security_hotspots": security_hotspots[:5],
        "risk_concentration_ratio": risk_concentration_ratio
    }