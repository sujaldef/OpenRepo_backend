#!/usr/bin/env python3
"""
🔬 DETAILED PIPELINE INSPECTION
Prints exact JSON structure of predictions and recommendations
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from services.pipeline.full_analysis_pipeline import run_full_pipeline


def inspect_pipeline(repo_path: str):
    """Inspect exact output structure"""
    print("\n" + "="*70)
    print("🔬 DETAILED PIPELINE INSPECTION")
    print("="*70)
    
    results = run_full_pipeline(repo_path)
    
    # Predictions
    predictions = results.get("prediction_report", {}).get("ai_analysis", [])
    print(f"\n📋 PREDICTIONS ({len(predictions)} items):")
    print(json.dumps(predictions, indent=2)[:1500] + "...\n")
    
    # Recommendations
    recommendations = results.get("repo_recommendations", [])
    print(f"\n📋 RECOMMENDATIONS ({len(recommendations)} items):")
    print(json.dumps(recommendations, indent=2)[:1500] + "...\n")
    
    # Top risky files
    top_risky = results.get("top_risky_files", [])
    print(f"\n📋 TOP RISKY FILES ({len(top_risky)} items):")
    print(json.dumps(top_risky, indent=2)[:1500] + "...\n")


if __name__ == "__main__":
    test_repo = "d:\\sujal\\dev\\Projects final\\openreponew\\OpenRepo\\openrepo_backend"
    inspect_pipeline(test_repo)
