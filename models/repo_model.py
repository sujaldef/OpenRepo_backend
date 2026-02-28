from pydantic import BaseModel
from datetime import datetime

class Repository(BaseModel):
    id: str | None = None
    user_id: str
    repo_url: str
    repo_name: str
    repo_owner: str | None = None
    branch: str = "main"

    last_analysis_status: str = "never"
    last_analyzed_at: datetime | None = None
    current_health_score: int | None = None

    detected_stack: str | None = None
    primary_language: str | None = None
    total_analyses: int = 0

    created_at: datetime = datetime.utcnow()
