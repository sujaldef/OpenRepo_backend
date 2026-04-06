from .metrics_engine import compute_metrics
from .defect_detection import analyze_file_defects


def run_static_analysis(file_path: str):

    metrics = compute_metrics(file_path)
    defect_result = analyze_file_defects(file_path)
    issues = defect_result.get("issues", [])

    # Add issue aggregates into metrics
    security_count = sum(1 for i in issues if i.get("type") == "Security")

    metrics["total_issue_count"] = len(issues)
    metrics["security_issue_count"] = security_count

    return {
        "file_path": file_path,
        "metrics": metrics,
        "issues": issues
    }