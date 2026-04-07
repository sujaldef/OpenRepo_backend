# 🎮 Controllers

**GitHub About:**
FastAPI route handlers managing API endpoints for authentication, repositories, analysis results, and predictions. Coordinates request/response flow between frontend and backend services.

---

## 📋 Overview

Controllers handle HTTP endpoints and route requests to appropriate services. Each controller manages a specific domain of the API.

---

## 📁 Files

### `auth_controller.py`
Handles user authentication, registration, and JWT token management.
- `POST /api/auth/login` - User login with JWT
- `POST /api/auth/register` - New user registration
- `GET /api/auth/me` - Current user info

### `error_controller.py`
Fetches and manages detected issues in repositories.
- `GET /api/repos/{id}/errors` - Get detected issues
- Integrates with issue detection ML models

### `prediction_controller.py`
Provides ML-powered predictions for vulnerability analysis.
- `GET /api/repos/{id}/predictions` - Get risk predictions
- `POST /api/repos/{id}/predict` - Run new predictions

### `recommendation_controller.py`
Generates actionable recommendations based on analysis.
- `GET /api/repos/{id}/recommendations` - Get suggestions
- Prioritizes recommendations by impact

### `repo_controller.py`
CRUD operations for repository management.
- `GET /api/repos` - List user repos
- `POST /api/repos` - Create new repo
- `GET /api/repos/{id}` - Get repo details
- `DELETE /api/repos/{id}` - Remove repo

### `structure_controller.py`
Analyzes and reports repository structure and metrics.
- `GET /api/repos/{id}/structure` - Get structure analysis
- Reports folder hierarchy, file distribution

### `summary_controller.py`
Provides comprehensive repository analysis summaries.
- `GET /api/repos/{id}/summary` - Full analysis report
- Aggregates issues, predictions, recommendations

---

## 🔄 Request Flow

```
Request
  ↓
Router (app.py)
  ↓
Controller (validates, formats request)
  ↓
Service (business logic)
  ↓
Model (DB operations)
  ↓
Response (formatted JSON)
```

---

## 🏗️ Pattern

Each controller follows this pattern:

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/endpoint", tags=["domain"])

@router.get("/")
def get_items():
    # Logic here
    return {"data": []}
```

---

## 📝 Notes

- All endpoints require authentication (JWT)
- Errors return proper HTTP status codes
- Responses are JSON-serialized
