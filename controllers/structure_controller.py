from fastapi import APIRouter
from bson import ObjectId
from app import repos
from services.structure.structure_analyzer import StructureAnalyzer
from services.structure.folder_tree_builder import build_folder_tree

router = APIRouter(prefix="/structure", tags=["Structure"])


@router.get("/{repo_id}")
def get_structure(repo_id: str):

    repo = repos.find_one({"_id": ObjectId(repo_id)})
    repo_path = repo["url"]

    analyzer = StructureAnalyzer()
    metrics = analyzer.analyze(repo_path)
    tree = build_folder_tree(repo_path)

    return {
        "metrics": metrics,
        "tree": tree
    }