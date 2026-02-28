# services/ml_engine/repo_llm_prediction_engine.py

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


SYSTEM_PROMPT = """
You are a senior AI engineering auditor.

Your job is to explain repository health to a developer.

For each insight:
- Clearly explain what is wrong.
- Explain how serious it is.
- Specify exact location (folders and files).
- Explain why it matters.
- Explain what happens if ignored.
- Explain what to fix first.
- Avoid generic advice.
- Be specific to provided data.
- Maximum 5 insights.
- Return ONLY valid JSON.

Required Format:

{
  "executive_summary": {
    "overall_health_score": 0,
    "primary_risk_driver": "",
    "risk_trend": ""
  },
  "ai_analysis": [
    {
      "priority_rank": 1,
      "title": "",
      "what_is_wrong": "",
      "how_serious": "High | Medium | Low",
      "where_exactly": {
        "primary_folder": "",
        "affected_files": []
      },
      "why_it_matters": "",
      "if_ignored": "",
      "what_to_fix_first": "",
      "estimated_effort": "Low | Medium | High",
      "confidence": 0.0
    }
  ]
}
"""


def generate_llm_repo_predictions(insight_summary):

    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not set in environment.")

    prompt = build_prompt(insight_summary)

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
    )

    result = response.json()

    content = result["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    metadata = {
        "model": result.get("model"),
        "usage": result.get("usage"),
        "finish_reason": result["choices"][0].get("finish_reason")
    }

    return parsed, metadata


def build_prompt(summary):

    return f"""
Repository Metrics:
{json.dumps(summary["repo_metrics"], indent=2)}

Structure Metrics:
{json.dumps(summary["structure_metrics"], indent=2)}

Top Risky Files:
{json.dumps(summary["top_risky_files"], indent=2)}

Security Hotspots:
{json.dumps(summary["security_hotspots"], indent=2)}

Risk Concentration Ratio:
{summary["risk_concentration_ratio"]}

Generate structured AI explanation.
Return only JSON.
"""