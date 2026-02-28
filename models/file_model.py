# models/file_model.py

from pydantic import BaseModel
from datetime import datetime
from typing import Dict


class File(BaseModel):
    repo_id: str
    path: str
    language: str
    size: int
    metrics: Dict

    created_at: datetime = datetime.utcnow()