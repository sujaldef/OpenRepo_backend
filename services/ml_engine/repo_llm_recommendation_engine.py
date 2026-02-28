# services/ml_engine/repo_llm_recommendation_engine.py

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def generate_llm_repo_recommendations(insight_summary: dict):

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

    try:
        content = result["choices"][0]["message"]["content"]

        parsed = json.loads(content)

        metadata = {
            "model": result.get("model"),
            "usage": result.get("usage"),
            "finish_reason": result["choices"][0].get("finish_reason")
        }

        return parsed, metadata

    except Exception:
        raise Exception(f"Invalid LLM response: {result}")


SYSTEM_PROMPT = """
You are a senior software architecture auditor.

STRICT RULES:
- You MUST reference actual file paths from the provided lists.
- If file arrays are non-empty, you MUST use them.
- Do NOT generate generic advice.
- Every recommendation MUST reference at least one affected file unless absolutely impossible.
- Maximum 6 recommendations.
- Return ONLY valid JSON.

Format:

{
  "recommendations": [
    {
      "title": "",
      "impact_level": "High | Medium | Low",
      "why": "",
      "affected_files": [],
      "recommended_action": "",
      "estimated_effort": "Low | Medium | High",
      "confidence": 0.0
    }
  ]
}
"""

def build_prompt(insight_summary):

    return f"""
Repository Risk Analytics:

Repo Metrics:
{json.dumps(insight_summary.get("repo_metrics", {}), indent=2)}

Structure Metrics:
{json.dumps(insight_summary.get("structure_metrics", {}), indent=2)}

Risk Concentration Ratio:
{insight_summary.get("risk_concentration_ratio", 0)}

Top Risky Files (MUST reference these if applicable):
{json.dumps(insight_summary.get("top_risky_files", []), indent=2)}

Security Hotspots (MUST reference if non-empty):
{json.dumps(insight_summary.get("security_hotspots", []), indent=2)}

Generate structured architectural recommendations grounded in the data.
Return only JSON.
"""