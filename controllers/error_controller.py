# controllers/error_controller.py

from fastapi import APIRouter
from app import error_reports

router = APIRouter(prefix="/errors", tags=["Errors"])


# ---------------------------
# GET ALL ERRORS FOR A REPO
# ---------------------------
@router.get("/repo/{repo_id}")
def get_repo_errors(repo_id: str):

    result = []

    for r in error_reports.find({"repo_id": repo_id}):
        r["_id"] = str(r["_id"])
        result.append(r)

    return result