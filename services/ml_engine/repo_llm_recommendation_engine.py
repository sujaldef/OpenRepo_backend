# services/ml_engine/repo_llm_recommendation_engine.py

import os
import requests
import json
import re
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TIMEOUT = 10  # seconds
GROQ_RETRIES = 2

SYSTEM_PROMPT = """
You are a senior software architecture auditor.

STRICT RULES:
- You MUST reference actual file paths from the provided lists.
- If file arrays are non-empty, you MUST use them.
- Do NOT generate generic advice.
- Every recommendation MUST reference at least one affected file unless absolutely impossible.
- MINIMUM 3 recommendations MUST be provided.
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


def safe_parse_json(content):
    """Safely parse JSON with fallback regex extraction."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.debug("JSON parsing failed, attempting regex extraction")
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                logger.warning("Regex extraction failed, returning None")
                return None
        logger.warning("No JSON object found in content")
        return None


def validate_recommendation(rec):
    """Validate recommendation has all required schema fields."""
    required_fields = [
        "title", "impact_level", "why", "affected_files",
        "recommended_action", "estimated_effort", "confidence"
    ]
    
    if not isinstance(rec, dict):
        logger.debug("Validation failed: recommendation is not a dict")
        return False
    
    valid = all(field in rec for field in required_fields)
    if not valid:
        missing = [f for f in required_fields if f not in rec]
        logger.debug(f"Validation failed: missing fields {missing}")
    
    return valid


def ensure_min_recommendations(data, insight_summary):
    """Ensure minimum 3 valid recommendations with quality filtering and fallback."""
    recs = data.get("recommendations", [])
    
    # Filter only valid recommendations with confidence >= 0.5
    valid_recs = [
        r for r in recs 
        if validate_recommendation(r) and r.get("confidence", 0) >= 0.5
    ]
    
    logger.debug(f"Found {len(valid_recs)} valid recommendations (out of {len(recs)})")
    
    if len(valid_recs) >= 3:
        # Already have enough, cap at 6 max
        data["recommendations"] = valid_recs[:6]
        logger.info(f"Using {len(data['recommendations'])} valid recommendations")
        return data
    
    # Need fallback to reach minimum 3
    logger.warning(f"Only {len(valid_recs)} valid recommendations, generating fallback")
    fallback = generate_fallback_recommendations(insight_summary)
    fallback_items = fallback.get("recommendations", [])
    
    # Combine and cap at 6
    combined = (valid_recs + fallback_items)[:6]
    data["recommendations"] = combined
    
    logger.info(f"Returning {len(combined)} recommendations (valid: {len(valid_recs)}, fallback: {len(fallback_items)})")
    return data


def generate_fallback_recommendations(insight_summary):
    """Generate fallback recommendations using dynamic risk-aware confidence."""
    top_files = insight_summary.get("top_risky_files", [])
    
    fallback_recs = []
    
    # 🔥 HARD FALLBACK - Handle empty top_risky_files
    if not top_files:
        logger.warning("No top_risky_files found, returning generic recommendations")
        return {
            "recommendations": [
                {
                    "title": "Improve overall code quality",
                    "impact_level": "Medium",
                    "why": "No high-risk files detected but improvements still possible",
                    "affected_files": [],
                    "recommended_action": "Add tests, improve structure, enforce linting",
                    "estimated_effort": "Medium",
                    "confidence": 0.7
                },
                {
                    "title": "Introduce automated testing",
                    "impact_level": "Medium",
                    "why": "Testing improves reliability",
                    "affected_files": [],
                    "recommended_action": "Setup unit + integration tests",
                    "estimated_effort": "Medium",
                    "confidence": 0.75
                },
                {
                    "title": "Refactor large modules",
                    "impact_level": "Low",
                    "why": "Improves maintainability",
                    "affected_files": [],
                    "recommended_action": "Break into smaller components",
                    "estimated_effort": "Medium",
                    "confidence": 0.65
                }
            ]
        }
    
    # Generate recommendations from top risky files
    for i, file in enumerate(top_files[:3]):
        risk = file.get('risk_score', 0.5)
        
        if risk > 0.7:
            action = "Immediately break into smaller, focused functions. Implement unit tests. Add detailed code comments."
            effort = "High"
            confidence = min(0.8 + risk / 10, 0.95)
        elif risk > 0.4:
            action = "Modularize code to reduce coupling. Add integration tests. Simplify conditional logic."
            effort = "Medium"
            confidence = 0.75 + (risk / 10)
        else:
            action = "Refactor for readability. Add docstrings. Implement unit tests."
            effort = "Medium"
            confidence = 0.65 + (risk / 10)
        
        fallback_recs.append({
            "title": f"Priority {i+1}: Refactor {file.get('file_path', 'File')} (Risk: {risk:.2f})",
            "impact_level": "High",
            "why": f"File has risk score {risk:.2f} and complexity {file.get('complexity', 0)}",
            "affected_files": [file.get('file_path', 'unknown')],
            "recommended_action": action,
            "estimated_effort": effort,
            "confidence": round(confidence, 2)
        })
    
    return {"recommendations": fallback_recs}


def build_prompt(insight_summary):
    """Build the prompt for LLM recommendations."""
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
Return only valid JSON.
"""


def generate_llm_repo_recommendations(insight_summary):
    """Generate LLM-based recommendations with robust fallback, quality validation, and exponential backoff."""
    
    # DEBUG: Check if top_risky_files is populated
    print("🔍 DEBUG - TOP_RISKY_FILES:", insight_summary.get("top_risky_files"))
    logger.debug(f"Top risky files: {insight_summary.get('top_risky_files')}")
    
    # Check if API key available
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set. Using fallback recommendation generation.")
        parsed = generate_fallback_recommendations(insight_summary)
        metadata = {
            "model": "fallback",
            "usage": None,
            "finish_reason": "fallback_generation",
            "source": "offline_fallback"
        }
        return parsed, metadata
    
    prompt = build_prompt(insight_summary)
    
    # Retry logic with exponential backoff
    for attempt in range(GROQ_RETRIES):
        try:
            logger.debug(f"Attempting LLM recommendation (attempt {attempt + 1}/{GROQ_RETRIES})")
            
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
                },
                timeout=GROQ_TIMEOUT
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid LLM response structure")
            
            content = result["choices"][0]["message"]["content"]
            parsed = safe_parse_json(content)
            
            if not parsed:
                raise ValueError("Failed to parse LLM response")
            
            # Enforce minimum recommendations with quality validation
            parsed = ensure_min_recommendations(parsed, insight_summary)
            
            logger.info(f"Successfully retrieved {len(parsed.get('recommendations', []))} recommendations from LLM")
            
            metadata = {
                "model": result.get("model"),
                "usage": result.get("usage"),
                "finish_reason": result["choices"][0].get("finish_reason"),
                "source": "llm"
            }
            
            return parsed, metadata
        
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.error(f"LLM recommendation attempt {attempt + 1} failed: {type(e).__name__}: {str(e)}")
            
            if attempt == GROQ_RETRIES - 1:
                # Last attempt failed, use fallback
                logger.warning("All LLM attempts exhausted. Activating offline fallback.")
                parsed = generate_fallback_recommendations(insight_summary)
                metadata = {
                    "model": "fallback",
                    "usage": None,
                    "finish_reason": "fallback_after_retries",
                    "source": "offline_fallback",
                    "error": str(e)
                }
                return parsed, metadata
            
            # Exponential backoff: 1.5s, 3s, etc.
            backoff = 1.5 * (attempt + 1)
            logger.debug(f"Backoff for {backoff} seconds before retry")
            time.sleep(backoff)
    
    # Fallback (should not reach here)
    logger.error("Unexpected: Retry loop completed without return")
    parsed = generate_fallback_recommendations(insight_summary)
    metadata = {"model": "fallback", "source": "offline_fallback"}
    return parsed, metadata
