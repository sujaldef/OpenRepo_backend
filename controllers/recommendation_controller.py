# controllers/recommendation_controller.py

from fastapi import APIRouter
from app import recommendation_reports

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{repo_id}")
def get_repo_recommendations(repo_id: str):

    result = recommendation_reports.find_one({"repo_id": repo_id})

    if not result:
        return {}
    
    # Transform for frontend: map 'recommendations' to 'items' for consistency
    return {
        "_id": str(result.get("_id")),
        "repo_id": repo_id,
        "items": result.get("recommendations", []),
        "repo_risk_score": result.get("repo_risk_score", 0),
        "structure_score": result.get("structure_score", 0),
        "recommendation_count": result.get("recommendation_count", 0),
        "llm_metadata": result.get("llm_metadata", {}),
        "created_at": result.get("created_at")
    }