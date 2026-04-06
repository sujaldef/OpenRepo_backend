from pydantic import BaseModel
from datetime import datetime

class StructureAssessment(BaseModel):
    id: str | None = None
    analysis_id: str

    structure_score: int
    has_proper_structure: bool
    missing_folders: str | None = None

    separation_of_concerns_score: int

    has_tests: bool
    test_coverage_percentage: float
    testability_score: int
    untested_critical_files: int
    test_framework: str | None = None

    has_readme: bool
    readme_quality_score: int
    has_api_docs: bool
    has_contributing_guide: bool
    comment_coverage_percentage: float
    has_gitignore: bool
    sensitive_files_exposed: int

    created_at: datetime = datetime.utcnow()
