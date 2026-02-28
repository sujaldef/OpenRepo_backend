# models/prediction_model.py

from pydantic import BaseModel
from typing import List
from datetime import datetime


class RiskFile(BaseModel):
    file_path: str
    risk_score: float
    risk_level: str  # low | medium | high


class PredictionReport(BaseModel):
    repo_id: str

    overall_risk: str
    average_risk_score: float

    top_risky_files: List[RiskFile]

    created_at: datetime = datetime.utcnow()