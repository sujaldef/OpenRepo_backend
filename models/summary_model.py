# models/summary_model.py

from pydantic import BaseModel
from typing import List
from datetime import datetime


class Summary(BaseModel):
    repo_id: str

    overall_score: int
    health_grade: str
    risk_level: str

    total_files: int
    files_analyzed: int

    total_issues: int
    critical_issues: int

    high_risk_files: int
    medium_risk_files: int
    low_risk_files: int

    technical_debt_hours: float
    maintainability_index: int

    security_score: int
    quality_score: int
    structure_score: int

    hotspot_files: List[str]

    created_at: datetime = datetime.utcnow()