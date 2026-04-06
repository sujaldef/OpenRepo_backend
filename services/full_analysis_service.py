# services/full_analysis_service.py

from bson import ObjectId
from datetime import datetime

from app import (
    repos,
    error_reports,
    prediction_reports,
    recommendation_reports,
    summaries
)

from services.pipeline.full_analysis_pipeline import run_full_pipeline


def run_full_analysis(repo_id: str):

    print("RUN_FULL_ANALYSIS CALLED")

    repo = repos.find_one({"_id": ObjectId(repo_id)})
    if not repo:
        print("Repo not found")
        return

    repo_path = repo["url"]

    try:
        results = run_full_pipeline(repo_path)

        file_results = results.get("files", [])
        repo_metrics = results.get("repo_metrics", {})
        structure_metrics = results.get("structure_metrics", {})
        recommendations = results.get("repo_recommendations", [])
        top_risky_files = results.get("top_risky_files", [])
        llm_metadata = results.get("llm_metadata", {})  # optional future use

        print("FILES COUNT:", len(file_results))

        # --------------------------------
        # Clear Old Data
        # --------------------------------
        error_reports.delete_many({"repo_id": repo_id})
        prediction_reports.delete_many({"repo_id": repo_id})
        recommendation_reports.delete_many({"repo_id": repo_id})
        summaries.delete_many({"repo_id": repo_id})

        total_issues = 0

        # --------------------------------
        # Save File-Level Analysis
        # --------------------------------
        for file in file_results:

            file_issues = file.get("issues", [])
            total_issues += len(file_issues)

            error_reports.insert_one({
                "repo_id": repo_id,
                "file_path": file.get("file_path"),
                "issues": file_issues,
                "metrics": file.get("metrics", {}),
                "risk_score": file.get("risk_score", 0),
                "risk_profile": file.get("risk_profile", {}),
                "created_at": datetime.utcnow()
            })

        # --------------------------------
        # Compute Risk Distribution %
        # --------------------------------
        high = 0
        medium = 0
        low = 0

        for f in file_results:
            risk = f.get("risk_score", 0)
            if risk > 0.25:
                high += 1
            elif risk > 0.12:
                medium += 1
            else:
                low += 1

        total_files = repo_metrics.get("total_files", 1)

        risk_distribution = {
            "high_percent": round((high / total_files) * 100, 2) if total_files else 0,
            "medium_percent": round((medium / total_files) * 100, 2) if total_files else 0,
            "low_percent": round((low / total_files) * 100, 2) if total_files else 0,
        }

        # --------------------------------
        # Extract Critical Focus
        # --------------------------------
        critical_file = top_risky_files[0] if top_risky_files else None
        top_recommendation = recommendations[0] if recommendations else None

        # --------------------------------
        # Save Summary (Executive View)
        # --------------------------------
        summaries.insert_one({

            "repo_id": repo_id,

            # Executive Health
            "overall_score": results.get("overall_score", 100),
            "repo_risk_score": results.get("repo_risk_score", 0),
            "structure_score": results.get("structure_score", 0),
            "avg_file_risk": repo_metrics.get("avg_risk", 0),

            # Immediate Focus
            "critical_file": {
                "file_path": critical_file.get("file_path"),
                "risk_score": critical_file.get("risk_score")
            } if critical_file else None,

            "top_recommendation": top_recommendation,

            # Risk Distribution
            "risk_distribution": risk_distribution,

            # Quality Snapshot
            "total_files": repo_metrics.get("total_files", 0),
            "total_issues": total_issues,
            "avg_complexity": repo_metrics.get("avg_complexity", 0),
            "avg_duplication": repo_metrics.get("avg_duplication", 0),
            "test_coverage_ratio": repo_metrics.get("test_coverage_ratio", 0),
            "security_issues": repo_metrics.get("security_issues", 0),

            # Structure Snapshot
            "avg_depth": structure_metrics.get("avg_depth", 0),
            "max_depth": structure_metrics.get("max_depth", 0),
            "folder_entropy": structure_metrics.get("folder_entropy", 0),

            "created_at": datetime.utcnow()
        })

        # --------------------------------
        # Save Prediction Report
        # --------------------------------
        # --------------------------------
# Save AI Prediction Report (NEW STRUCTURE)
# --------------------------------
        prediction_reports.insert_one({
    "repo_id": repo_id,
    # LLM AI Predictions
    **results.get("prediction_report", {}),
    # Raw file risk data for frontendRiskHotspots component
    "top_risky_files": top_risky_files,
    "supporting_stats": {
        "repo_risk_score": results.get("repo_risk_score"),
        "structure_score": results.get("structure_score"),
        "total_files": repo_metrics.get("total_files"),
        "total_issues": total_issues
    },
    "llm_metadata": results.get("prediction_metadata", {}),
    "created_at": datetime.utcnow()
})

        # --------------------------------
        # Save Recommendation Report (NEW STRUCTURE)
        # --------------------------------
        recommendation_reports.insert_one({
            "repo_id": repo_id,
            "recommendations": recommendations,   # new structured LLM output
            "repo_risk_score": results.get("repo_risk_score", 0),
            "structure_score": results.get("structure_score", 0),
            "recommendation_count": len(recommendations),
            "llm_metadata": results.get("recommendation_metadata", {}), # future extensibility
            "created_at": datetime.utcnow()
        })

        # --------------------------------
        # Update Repo Status
        # --------------------------------
        repos.update_one(
            {"_id": ObjectId(repo_id)},
            {"$set": {"analysis_status": "completed"}}
        )

        print("ANALYSIS COMPLETED SUCCESSFULLY")

    except Exception as e:

        print("FULL ANALYSIS ERROR:", e)

        repos.update_one(
            {"_id": ObjectId(repo_id)},
            {"$set": {"analysis_status": "failed"}}
        )