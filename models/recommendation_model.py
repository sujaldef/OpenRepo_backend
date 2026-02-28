# models/recommendation_model.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RecommendationItem(BaseModel):
    file_path: str
    title: str
    description: str
    priority: str  # low | medium | high | critical
    effort: str    # low | medium | high

    suggested_change: Optional[str] = None
    code_example: Optional[str] = None
    doc_link: Optional[str] = None


class RecommendationReport(BaseModel):
    repo_id: str

    total_recommendations: int
    recommendations: List[RecommendationItem]

    created_at: datetime = datetime.utcnow()