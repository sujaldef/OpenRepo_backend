# controllers/summary_controller.py

from fastapi import APIRouter
from app import summaries

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/{repo_id}")
def get_summary(repo_id: str):

    summary = summaries.find_one({"repo_id": repo_id})

    if not summary:
        return {}

    summary["_id"] = str(summary["_id"])
    return summary