# models/error_model.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ErrorItem(BaseModel):
    line: int
    type: str
    severity: str  # "error" | "warning" | "info"
    message: str
    reason: Optional[str] = None
    fix_hint: Optional[str] = None


class ErrorReport(BaseModel):
    repo_id: str
    file_path: str

    total_errors: int
    items: List[ErrorItem]

    risk_score: float | None = None
    metrics: dict | None = None

    created_at: datetime = datetime.utcnow()