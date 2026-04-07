# ⚙️ Services

**GitHub About:**
Core business logic layer. Orchestrates analysis pipelines, ML model inference, and data processing. Connects controllers to models and AI engines.

---

## 📋 Overview

Services implement business logic and orchestration. They coordinate between controllers, models, and specialized analysis engines.

---

## 📁 Structure

```
services/
├── analysis_service.py           # General analysis orchestration
├── full_analysis_service.py      # End-to-end analysis pipeline
│
├── core_analysis/                # Code quality analysis
│   ├── repo_analyzer.py          # Repository structure analysis
│   ├── defect_detection.py       # Bug/defect detection
│   └── ...
│
├── ml_engine/                    # Machine learning inference
│   ├── repo_insight_engine.py    # Core ML predictions
│   ├── repo_risk_model.py        # Risk scoring
│   ├── repo_llm_prediction_engine.py  # LLM-based predictions
│   ├── repo_llm_recommendation_engine.py # LLM recommendations
│   ├── issue_classifier.py       # Issue categorization
│   └── ...
│
├── pipeline/                     # Analysis pipelines
│   ├── issue_pipeline.py         # Issue detection pipeline
│   ├── prediction_pipeline.py    # Prediction pipeline
│   └── ...
│
└── structure/                    # Repository structure analysis
    ├── structure_analyzer.py     # Folder/file hierarchy
    └── ...
```

---

## 🔑 Key Services

### `analysis_service.py`
Coordinates general code analysis workflows.
- Kicks off analysis jobs
- Aggregates results
- Handles caching

### `full_analysis_service.py`
End-to-end analysis orchestration for complete repository scan.
- Runs all analysis components
- Combines results into summary
- Stores in database

### Core Analysis: `core_analysis/`
**repo_analyzer.py** - Analyzes repository structure
- Extracts file hierarchy
- Calculates metrics per file
- Identifies high-risk areas

### ML Engine: `ml_engine/`
**repo_insight_engine.py** - Core ML inference
- Loads trained models
- Generates predictions
- Scores risk levels

**repo_risk_model.py** - Risk assessment
- Calculates overall repo risk
- Prioritizes issues
- Generates scores

**repo_llm_prediction_engine.py** - LLM-based predictions
- Uses language models for vulnerability detection
- Generates AI-powered insights
- Returns confidence scores

**repo_llm_recommendation_engine.py** - Smart recommendations
- Generates actionable suggestions
- Prioritizes by impact
- Estimates effort/time

### Pipeline: `pipeline/`
Specialized analysis workflows
- **issue_pipeline.py** - Issue detection
- **prediction_pipeline.py** - ML predictions
- **recommendation_pipeline.py** - Recommendations

### Structure Analysis: `structure/`
**structure_analyzer.py** - Repository organization analysis
- Analyzes folder hierarchy
- Identifies structure issues
- Calculates complexity metrics

---

## 🔄 Typical Flow

```
API Request (Controller)
  ↓
Service.analyze_repository()
  ↓
├─ core_analysis.analyze() → detect issues
├─ ml_engine.predict() → ML predictions
├─ llm_recommendation_engine.generate() → suggestions
└─ structure_analyzer.analyze() → structure insights
  ↓
Aggregate & store results
  ↓
Return to Controller
  ↓
API Response
```

---

## 🤖 ML Models Used

- **Issue Classification**: Categorizes bugs into types
- **Risk Prediction**: Predicts vulnerability likelihood
- **Structure Assessment**: Evaluates code organization
- **LLM Inference**: Uses language models for insights

---

## 💾 Data Handling

Services:
- Accept raw repository data
- Process and transform data
- Call ML models for inference
- Format results for response
- Handle errors gracefully

---

## 🎯 Design Pattern

```python
from services.ml_engine import repo_insight_engine

# In a service
predictions = await repo_insight_engine.predict(repo_files)
recommendations = await recommendation_engine.generate(analysis_results)
```

---

## 📝 Notes

- All services are async-ready
- Handle errors with proper exceptions
- Log important operations
- Cache results when possible
