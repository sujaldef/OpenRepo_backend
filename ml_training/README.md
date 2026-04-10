# 🤖 ML Training

**GitHub About:**
Dataset preparation, model training scripts, and ML pipeline. Trains supervised models for issue detection, risk prediction, and code analysis.

---

## 📋 Overview

This module handles all machine learning aspects: data collection, preprocessing, training, and model evaluation. Outputs trained models for production use.

---

## 📁 Structure

```
ml_training/
├── Training Scripts (train_*.py)
├── Dataset Builders (build_*.py)
├── Dataset Balancing (dataset_balancing/)
├── Datasets (datasets/)
├── Raw Datasets (raw_datasets/)
├── Saved Models (saved_models/)
├── Feature Engineering (feature_engineering.py)
└── Analysis & Evaluation
```

---

## 🔑 Key Files

### Training Scripts

**train_issue_model.py** - Issue classification model

- Trains model to categorize issues by type
- Output: `issue_classifier.pkl`
- Accuracy target: >85%

**train_repo_model.py** - Repository-level analysis

- Models overall repo characteristics
- Output: `repo_model.pkl`
- Predicts repo health metrics

**train_risk_regressor.py** - Risk scoring model

- Continuous risk score prediction (0-1)
- Output: `risk_model.pkl`
- Regression-based approach

**train_structure_model.py** - Code structure assessment

- Evaluates repository organization
- Output: `structure_model.pkl`
- Analyzes code layout patterns

### Dataset Builders

**build_issue_dataset.py**

- Collects and labels issue data
- Output: `issue_dataset.csv`

**build_repo_dataset.py**

- Repository-level feature extraction
- Output: `repo_dataset.csv`

**build_structure_dataset.py**

- Repository structure features
- Output: `structure_dataset.csv`

**build_mern_dataset.py** / **build_clang_dataset.py** / **build_python_dataset.py**

- Language-specific datasets
- Extracted from open-source repos

### Dataset Balancing

**balance_mern_dataset.py** / **balance_python_dataset.py** / **balance_clang_dataset.py**

- Handles class imbalance
- Balances positive/negative samples
- Output: `*_balanced.csv`

**clean\_\*.py**

- Data cleaning & preprocessing
- Removes duplicates, outliers
- Output: `*_cleaned.csv`

### Feature Engineering

**feature_engineering.py**

- Creates derived features
- Normalizes inputs
- Selects important features
- Output: enhanced datasets

### Analysis & Evaluation

**analyze_dataset.py**

- Exploratory data analysis
- Statistics and distributions
- Data quality checks

**analyze_models.py**

- Model performance comparison
- Accuracy, precision, recall metrics
- Identifies best models

**evaluate_model.py**

- Cross-validation
- Test set evaluation
- Performance benchmarking

---

## 📊 Datasets

### Issue Dataset

- **Size**: ~105 MB
- **Records**: 50,000+
- **Labels**: Issue type (Critical, Error, Warning)
- **Features**: File path, line number, code context

### Repository Datasets

- **MERN**: JavaScript/Node.js repos
- **Python**: Python projects
- **C/Lang**: C/C++ codebases

### Processed Datasets

| Dataset                 | Purpose              | Records |
| ----------------------- | -------------------- | ------- |
| `issue_dataset.csv`     | Issue classification | 50,000+ |
| `repo_dataset.csv`      | Repo-level analysis  | 1,000+  |
| `structure_dataset.csv` | Structure assessment | 5,000+  |
| `*_cleaned.csv`         | Quality-checked data | Varies  |
| `*_balanced.csv`        | Class-balanced data  | Varies  |

---

## 🤖 Saved Models

```
saved_models/
├── issue_classifier.pkl     # Issue type classification
├── repo_model.pkl           # Repository analysis
├── risk_model.pkl           # Risk scoring (regression)
├── structure_model.pkl      # Structure assessment
└── folder_model.pkl         # Folder-level analysis
```

**Format**: Pickle (Python's serialized objects)

---

## 🔄 Pipeline

```
Raw Data (Open Source Repos)
  ↓
Dataset Builder (extract features, label)
  ↓
Cleaned Dataset (remove noise, duplicates)
  ↓
Balanced Dataset (handle class imbalance)
  ↓
Feature Engineering (create derived features)
  ↓
Model Training (fit on training set)
  ↓
Evaluation (validate on test set)
  ↓
Saved Model (.pkl files)
  ↓
Production Inference (in services/)
```

---

## 🛠️ Usage

### Training a Model

```bash
python train_issue_model.py
```

### Building Dataset

```bash
python build_issue_dataset.py
```

### Balancing Data

```bash
python dataset_balancing/balance_mern_dataset.py
```

### Evaluating Models

```bash
python evaluate_model.py
```

---

## 📈 Performance Metrics

Models target:

- **Issue Classification**: 85%+ accuracy
- **Risk Prediction**: R² > 0.75
- **Structure Analysis**: 80%+ accuracy

---

## ⚙️ Configuration

Edit training scripts to adjust:

- `test_size` - Train/test split ratio
- `random_state` - Reproducibility seed
- `features_to_use` - Feature selection
- `model_hyperparameters` - ML hyperparameters

---

## 🔍 Troubleshooting

**Memory Issues**: Datasets are large. Use batch processing or sample subsets.

**Class Imbalance**: Run balancing scripts before training.

**Model Accuracy**: Adjust hyperparameters or collect more training data.

---

## 📝 Notes

- All datasets use `.csv` format
- Models saved as Python `.pkl` files
- Training is batch-based for efficiency
