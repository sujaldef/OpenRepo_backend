# 🗂️ Models

**GitHub About:**
Database models and schemas using FastAPI Pydantic. Defines data structure for users, repositories, analysis results, and ML predictions with validation.

---

## 📋 Overview

Models define database schemas and data structures using **Pydantic** and **MongoDB ODM**. Each model represents a domain entity with validation rules.

---

## 📁 Files

### `user_model.py`

Represents user accounts with authentication & profile data.

- `username` - Unique user identifier
- `email` - Contact email
- `password` - Hashed password
- `bio` - User profile bio
- `avatar` - Profile picture URL

### `repo_model.py`

Repository metadata and analysis status.

- `name` - Repository name
- `url` - Repository URL
- `owner_id` - Creator user ID
- `type` - Language (Python, JavaScript, etc.)
- `status` - Analysis status (Pending, Complete)
- `score` - Overall quality score

### `error_model.py`

Detected issues, bugs, and security problems.

- `file_path` - Path to file with issue
- `line_number` - Line number
- `severity` - Critical, Error, Warning
- `message` - Description of issue
- `issue_type` - Category (Security, Logic, Style)

### `prediction_model.py`

ML model predictions for vulnerability detection.

- `file_path` - Affected file
- `prediction` - Predicted issue type
- `confidence` - Confidence score (0-100)
- `risk_level` - High, Medium, Low
- `description` - Prediction rationale

### `recommendation_model.py`

Improvement suggestions with implementation guidance.

- `title` - Recommendation title
- `description` - Detailed suggestion
- `priority` - Priority level (1-5)
- `estimated_effort` - Time estimate (minutes)
- `impact_score` - Expected impact score

### `file_model.py`

Individual file metadata for repositories.

- `path` - File path in repo
- `extension` - File type (.py, .js, etc.)
- `language` - Programming language
- `lines_of_code` - LOC count
- `complexity` - Cyclomatic complexity

### `summary_model.py`

Aggregated analysis summary for repositories.

- `total_issues` - Count of all issues
- `critical_count` - Count of critical issues
- `avg_severity` - Average severity score
- `recommendations_count` - Total recommendations
- `overall_score` - Repo health score (0-100)

---

## 🔗 Relationships

```
User
  ├── Repository (1-to-many)
  │   ├── File (1-to-many)
  │   ├── Error (1-to-many)
  │   ├── Prediction (1-to-many)
  │   ├── Recommendation (1-to-many)
  │   └── Summary (1-to-1)
```

---

## 🔐 Validation

Models include:

- Required field validation
- Type checking
- Field length constraints
- Email validation
- Enum validation for status/severity

---

## 🗄️ Persistence

- **Database**: MongoDB
- **ODM**: Beanie (MongoDB + Pydantic)
- **Indexes**: Applied on commonly queried fields

---

## 📝 Usage Example

```python
from models.user_model import User

# Create
user = User(username="john", email="john@example.com", password="hashed")
await user.insert()

# Read
user = await User.find_one({"email": "john@example.com"})

# Delete
await user.delete()
```
