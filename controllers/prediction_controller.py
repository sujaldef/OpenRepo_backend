# controllers/prediction_controller.py

from fastapi import APIRouter
from app import prediction_reports

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("/{repo_id}")
def get_repo_predictions(repo_id: str):

    result = prediction_reports.find_one({"repo_id": repo_id})

    if result:
        result["_id"] = str(result["_id"])

    return result or {}