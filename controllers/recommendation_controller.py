# controllers/recommendation_controller.py

from fastapi import APIRouter
from app import recommendation_reports

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{repo_id}")
def get_repo_recommendations(repo_id: str):

    result = recommendation_reports.find_one({"repo_id": repo_id})

    if result:
        result["_id"] = str(result["_id"])

    return result or {}