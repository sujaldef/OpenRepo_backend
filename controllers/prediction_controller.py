# controllers/prediction_controller.py

from fastapi import APIRouter
from app import prediction_reports

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("/{repo_id}")
def get_repo_predictions(repo_id: str):

    result = prediction_reports.find_one({"repo_id": repo_id})

    if not result:
        return {}
    
    # Transform data for frontend compatibility
    top_risky = result.get("top_risky_files", [])
    
    # Transform each file: add 'relative_path' alias for 'file_path'
    transformed_files = []
    for file in top_risky:
        file_copy = dict(file)
        # Add relative_path if it doesn't exist (frontend expects this)
        if "relative_path" not in file_copy and "file_path" in file_copy:
            file_copy["relative_path"] = file_copy["file_path"]
        transformed_files.append(file_copy)
    
    # Return data for RiskHotspots component which expects 'top_risky_files'
    return {
        "_id": str(result.get("_id")),
        "repo_id": repo_id,
        "top_risky_files": transformed_files,
        "ai_analysis": result.get("ai_analysis", []),
        "executive_summary": result.get("executive_summary", {}),
        "supporting_stats": result.get("supporting_stats", {}),
        "llm_metadata": result.get("llm_metadata", {}),
        "created_at": result.get("created_at")
    }