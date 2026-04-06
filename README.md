# OpenRepo Backend 🚀

AI-powered code analysis backend for OpenRepo - providing intelligent insights on code quality, issues, predictions, and recommendations.

## 📋 Overview

OpenRepo Backend is a FastAPI-based REST API that performs comprehensive code analysis using machine learning and static analysis techniques. It provides:

- **Error Detection**: Identifies bugs, security issues, and code smells
- **AI Predictions**: Machine learning-based code quality predictions
- **Recommendations**: Actionable improvement suggestions powered by LLMs
- **Code Metrics**: Static analysis metrics (complexity, test coverage, etc.)
- **Repository Insights**: Holistic repository health analysis

## 🏗️ Architecture

```
OpenRepo Backend
├── controllers/          # API endpoints & route handlers
│   ├── auth_controller.py
│   ├── repo_controller.py
│   ├── error_controller.py
│   ├── prediction_controller.py
│   ├── recommendation_controller.py
│   └── summary_controller.py
│
├── services/            # Business logic & analysis engines
│   ├── full_analysis_service.py (Main orchestrator)
│   ├── core_analysis/   (Defect, dependency, metrics, etc.)
│   ├── ml_engine/       (LLM predictions, recommendations)
│   └── pipeline/        (Analysis pipeline)
│
├── models/              # Data models & schemas
│   ├── user_model.py
│   ├── repo_model.py
│   ├── error_model.py
│   ├── prediction_model.py
│   └── recommendation_model.py
│
├── ml_training/         # ML model training & datasets
│   ├── training/        (Model training scripts)
│   ├── dataset_builders/ (Data preprocessing)
│   └── dataset_balancing/ (Dataset optimization)
│
└── utils/               # Utilities (auth, JWT, helpers)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud)
- FastAPI & dependencies (see requirements.txt)

### Installation

```bash
# Clone the repository
git clone https://github.com/sujaldef/OpenRepo_backend.git
cd OpenRepo_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development server with auto-reload
uvicorn app:app --reload

# Production server
uvicorn app:app --host 0.0.0.0 --port 8000
```

Server will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs** (Swagger UI)

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token

### Repositories
- `GET /api/repos` - List user repositories
- `POST /api/repos` - Create repository entry
- `GET /api/repos/:repoId` - Get repository details
- `DELETE /api/repos/:repoId` - Delete repository

### Analysis
- `POST /api/repos/:repoId/analyze` - Trigger full analysis
- `GET /api/repos/:repoId/errors` - Get detected errors
- `GET /api/repos/:repoId/predictions` - Get predictions
- `GET /api/repos/:repoId/recommendations` - Get recommendations
- `GET /api/repos/:repoId/summary` - Get analysis summary

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Database
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=code_audit

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# OpenAI (for LLM features)
OPENAI_API_KEY=your-openai-key

# Flask/Debugging
DEBUG=true
```

## 📊 Database Schema

### Collections

- **users**: User accounts and authentication
- **repos**: Repository information
- **files**: Source code files metadata
- **error_reports**: Detected errors/issues
- **prediction_reports**: ML predictions
- **recommendation_reports**: AI recommendations
- **summaries**: Repository analysis summaries

## 🧠 ML Models

Pre-trained models for code analysis:

- **Python Model**: Defect detection for Python
- **JavaScript Model**: Issue detection for JS/TypeScript
- **C/C++ Model**: Code quality analysis for C/C++
- **MERN Model**: React/Node.js stack analysis
- **Risk Model**: Security risk regression model

Models are stored in `ml_training/saved_models/` (not in git, use Git LFS or download separately).

## 📈 Analysis Pipeline

```
1. Code Upload
   ↓
2. Static Analysis
   ├── Defect Detection
   ├── Dependency Audit
   ├── Duplication Analysis
   └── Metrics Calculation
   ↓
3. ML Classification
   ├── Issue Classification
   ├── Severity Prediction
   └── Risk Assessment
   ↓
4. LLM Insights
   ├── Predictions (with confidence scores)
   └── Recommendations (with priorities)
   ↓
5. Report Generation
   └── Summary & Insights
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=. tests/

# Specific test file
pytest tests/test_analysis.py
```

## 🔐 Security Features

- JWT-based authentication
- CORS middleware for cross-origin requests
- Input validation & sanitization
- Rate limiting (optional)
- Secure password hashing (bcrypt)

## 📦 Dependencies

Key dependencies (see requirements.txt for full list):

- **fastapi**: Web framework
- **pymongo**: MongoDB driver
- **python-jose**: JWT handling
- **pydantic**: Data validation
- **scikit-learn**: ML models
- **transformers**: NLP models
- **openai**: LLM integration

## 🚨 Troubleshooting

### MongoDB Connection Error
```bash
# Make sure MongoDB is running
mongod --dbpath /path/to/data

# Or use MongoDB Atlas Cloud
# Update MONGO_URI in .env
```

### Large File Issues
The repository uses `.gitignore` to exclude large dataset files:
- `ml_training/datasets/` (>800MB)
- `ml_training/raw_datasets/` (>400MB)

To download datasets:
```bash
# Download from your storage
# Or rebuild from source data
python ml_training/dataset_builders/build_python_dataset.py
```

### LLM API Issues
Ensure `OPENAI_API_KEY` is set:
```bash
export OPENAI_API_KEY="sk-..."
# or set in .env file
```

## 📝 Development

### Adding New Analysis Feature

1. Create analysis module in `services/core_analysis/`
2. Implement analysis logic
3. Update `full_analysis_service.py` to call it
4. Create API endpoint in `controllers/`
5. Update data models if needed
6. Add tests

### Adding New ML Model

1. Add model to `models/` directory
2. Create training script in `ml_training/training/`
3. Save trained model to `ml_training/saved_models/`
4. Update `repo_insight_engine.py` to use it
5. Document model performance

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is part of the OpenRepo suite.

## 🙋 Support

- 📧 Email: support@openrepo.dev
- 🐛 Issues: [GitHub Issues](https://github.com/sujaldef/OpenRepo_backend/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/sujaldef/OpenRepo_backend/discussions)

## 🎯 Roadmap

- [ ] Add Docker support for easy deployment
- [ ] Implement caching layer (Redis)
- [ ] Add WebSocket support for real-time updates
- [ ] Extend language support (Go, Rust, Java)
- [ ] Performance optimization & async improvements
- [ ] Enhanced reporting & visualization APIs
- [ ] Integration tests with frontend

---

**Made with ❤️ by the OpenRepo team**

**Version:** 1.0.0
**Last Updated:** April 7, 2026
