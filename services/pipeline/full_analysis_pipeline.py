# services/pipeline/full_analysis_pipeline.py

from services.core_analysis.repo_analyzer import analyze_repo
from services.ml_engine.risk_model import RiskModel
from services.ml_engine.repo_recommendation_engine import generate_repo_recommendations
from services.ml_engine.repo_risk_model import RepoRiskModel
from services.structure.structure_analyzer import StructureAnalyzer
from services.structure.structure_model import StructureModel
from services.ml_engine.repo_insight_engine import build_repo_insight_summary
from services.ml_engine.repo_llm_prediction_engine import generate_llm_repo_predictions
from services.ml_engine.repo_llm_recommendation_engine import generate_llm_repo_recommendations


risk_model = RiskModel()
repo_model = RepoRiskModel()
structure_model = StructureModel()
structure_analyzer = StructureAnalyzer()


def run_full_pipeline(repo_path: str):
    # ───────────────────────────────────────────────
    # 1️⃣ Static Analysis
    # ───────────────────────────────────────────────
    file_results = analyze_repo(repo_path)

    # ───────────────────────────────────────────────
    # 2️⃣ File-Level ML Risk Prediction
    # ───────────────────────────────────────────────
    for file in file_results:
        metrics = file.get("metrics", {})
        risk_profile = risk_model.predict(metrics)
        file["risk_profile"] = risk_profile
        file["risk_score"] = risk_profile["overall_risk"]

    # ───────────────────────────────────────────────
    # 3️⃣ Rank Risky Files
    # ───────────────────────────────────────────────
    top_risky = sorted(
        file_results,
        key=lambda x: x.get("risk_score", 0),
        reverse=True
    )[:5]

    # ───────────────────────────────────────────────
    # 4️⃣ Repo-Level Metric Aggregation
    # ───────────────────────────────────────────────
    repo_metrics = compute_repo_metrics(file_results)

    if repo_metrics:
        repo_risk_score = repo_model.predict(repo_metrics)
        repo_metrics["repo_risk_score"] = round(repo_risk_score, 4)
    else:
        repo_risk_score = 0

    # ───────────────────────────────────────────────
    # 5️⃣ Folder Structure Analysis + ML
    # ───────────────────────────────────────────────
    structure_metrics = structure_analyzer.analyze(repo_path)

    if structure_model.is_available() and structure_metrics:
        structure_score = structure_model.predict(structure_metrics)
    else:
        structure_score = 0

    structure_metrics["structure_score"] = round(structure_score, 4)

    # ───────────────────────────────────────────────
    # 6️⃣ Build Insight Summary for LLM
    # ───────────────────────────────────────────────
    insight_summary = build_repo_insight_summary(
        file_results,
        repo_metrics,
        structure_metrics
    )

    # ───────────────────────────────────────────────
    # 7️⃣ LLM-based Predictions / Narrative
    # ───────────────────────────────────────────────
    prediction_response, prediction_metadata = generate_llm_repo_predictions(insight_summary)

    # ───────────────────────────────────────────────
    # 8️⃣ LLM-based Recommendations
    # ───────────────────────────────────────────────
    parsed_response, recommendation_metadata = generate_llm_repo_recommendations(insight_summary)

    repo_recommendations = parsed_response.get("recommendations", [])

    # ───────────────────────────────────────────────
    # 9️⃣ Final Ensemble Health Score
    # ───────────────────────────────────────────────
    overall_score = compute_overall_score(
        file_results,
        repo_risk_score,
        structure_score
    )

    return {
        "files": file_results,
        "overall_score": overall_score,
        "top_risky_files": top_risky,
        "repo_metrics": repo_metrics,
        "repo_recommendations": repo_recommendations,
        "repo_risk_score": repo_risk_score,
        "structure_metrics": structure_metrics,
        "structure_score": structure_score,
        # LLM outputs
        "prediction_report": prediction_response,
        "prediction_metadata": prediction_metadata,
        "recommendation_metadata": recommendation_metadata
    }


def compute_repo_metrics(file_results):
    total_files = len(file_results)
    if total_files == 0:
        return {}

    avg_risk = sum(
        f.get("risk_score", 0) for f in file_results
    ) / total_files

    avg_complexity = sum(
        f.get("metrics", {}).get("cyclomatic_complexity", 0) for f in file_results
    ) / total_files

    total_issues = sum(
        f.get("metrics", {}).get("total_issue_count", 0) for f in file_results
    )

    security_issues = sum(
        f.get("metrics", {}).get("security_issue_count", 0) for f in file_results
    )

    avg_duplication = sum(
        f.get("metrics", {}).get("duplication_ratio", 0) for f in file_results
    ) / total_files

    test_coverage_ratio = sum(
        f.get("metrics", {}).get("has_tests", 0) for f in file_results
    ) / total_files

    return {
        "total_files": total_files,
        "avg_risk": round(avg_risk, 4),
        "avg_complexity": round(avg_complexity, 2),
        "total_issues": total_issues,
        "security_issues": security_issues,
        "avg_duplication": round(avg_duplication, 4),
        "test_coverage_ratio": round(test_coverage_ratio, 2)
    }


def compute_overall_score(file_results, repo_risk, structure_risk):
    if not file_results:
        return 100.0

    avg_file_risk = sum(
        f.get("risk_score", 0) for f in file_results
    ) / len(file_results)

    # Weighted ensemble
    combined_risk = (
        avg_file_risk * 0.60 +
        repo_risk     * 0.25 +
        structure_risk * 0.15
    )

    health_score = 100 - (combined_risk * 100)

    return round(max(0, min(health_score, 100)), 2)