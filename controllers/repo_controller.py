# controllers/repo_controller.py

from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime

from app import repos, summaries
from utils.auth_dependency import get_current_user
from services.full_analysis_service import run_full_analysis

router = APIRouter(prefix="/repos", tags=["Repos"])


# ---------------------------
# CREATE REPO
# ---------------------------
@router.post("/")
def create_repo(
    name: str,
    url: str,
    user_id: str = Depends(get_current_user)
):

    repo = {
        "user_id": user_id,
        "name": name,
        "url": url,
        "analysis_status": "idle",
        "created_at": datetime.utcnow()
    }

    result = repos.insert_one(repo)
    return {"repo_id": str(result.inserted_id)}


# ---------------------------
# GET USER REPOS
# ---------------------------
@router.get("/")
def get_user_repos(user_id: str = Depends(get_current_user)):

    result = []
    for r in repos.find({"user_id": user_id}):
        r["_id"] = str(r["_id"])
        result.append(r)

    return result


# ---------------------------
# GET ONE REPO
# ---------------------------
@router.get("/{repo_id}")
def get_repo(repo_id: str):

    repo = repos.find_one({"_id": ObjectId(repo_id)})
    if not repo:
        raise HTTPException(404, "Repo not found")

    repo["_id"] = str(repo["_id"])

    summary = summaries.find_one({"repo_id": repo_id})
    repo["summary"] = summary or {}

    return repo


# ---------------------------
# DELETE REPO
# ---------------------------
@router.delete("/{repo_id}")
def delete_repo(repo_id: str):

    repos.delete_one({"_id": ObjectId(repo_id)})
    return {"message": "Repo deleted"}


# ---------------------------
# START FULL ANALYSIS
# ---------------------------
@router.post("/{repo_id}/analyze")
def analyze_repository(repo_id: str):

    repo = repos.find_one({"_id": ObjectId(repo_id)})
    if not repo:
        raise HTTPException(404, "Repo not found")

    repos.update_one(
        {"_id": ObjectId(repo_id)},
        {"$set": {"analysis_status": "running"}}
    )

    try:
        run_full_analysis(repo_id)

        return {
            "analysis_status": "completed"
        }

    except Exception as e:

        repos.update_one(
            {"_id": ObjectId(repo_id)},
            {"$set": {"analysis_status": "failed"}}
        )

        raise HTTPException(500, str(e))


# ---------------------------
# ANALYSIS STATUS
# ---------------------------
@router.get("/{repo_id}/status")
def get_analysis_status(repo_id: str):

    repo = repos.find_one({"_id": ObjectId(repo_id)})
    if not repo:
        raise HTTPException(404, "Repo not found")

    return {
        "analysis_status": repo.get("analysis_status", "idle")
    }