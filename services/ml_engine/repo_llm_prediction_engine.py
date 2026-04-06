# services/ml_engine/repo_llm_prediction_engine.py

import os
import json
import re
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TIMEOUT = 10  # seconds
GROQ_RETRIES = 2

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
- MINIMUM 3 insights MUST be provided.
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


def validate_prediction(pred):
    """Validate prediction has all required schema fields."""
    required_fields = [
        "priority_rank", "title", "what_is_wrong", "how_serious",
        "where_exactly", "why_it_matters", "if_ignored", "what_to_fix_first",
        "estimated_effort", "confidence"
    ]
    
    if not isinstance(pred, dict):
        logger.debug("Validation failed: prediction is not a dict")
        return False
    
    valid = all(field in pred for field in required_fields)
    if not valid:
        missing = [f for f in required_fields if f not in pred]
        logger.debug(f"Validation failed: missing fields {missing}")
    
    return valid


def ensure_min_predictions(data, insight_summary):
    """Ensure minimum 3 valid predictions with quality filtering and fallback."""
    analysis = data.get("ai_analysis", [])
    
    # Filter only valid predictions with confidence >= 0.5
    valid_predictions = [
        p for p in analysis 
        if validate_prediction(p) and p.get("confidence", 0) >= 0.5
    ]
    
    logger.debug(f"Found {len(valid_predictions)} valid predictions (out of {len(analysis)})")
    
    if len(valid_predictions) >= 3:
        # Already have enough, cap at 5 max
        data["ai_analysis"] = valid_predictions[:5]
        logger.info(f"Using {len(data['ai_analysis'])} valid predictions")
        return data
    
    # Need fallback to reach minimum 3
    logger.warning(f"Only {len(valid_predictions)} valid predictions, generating fallback")
    fallback = generate_fallback_predictions(insight_summary)
    fallback_items = fallback.get("ai_analysis", [])
    
    # Combine and cap at 5
    combined = (valid_predictions + fallback_items)[:5]
    data["ai_analysis"] = combined
    
    logger.info(f"Returning {len(combined)} predictions (valid: {len(valid_predictions)}, fallback: {len(fallback_items)})")
    return data


def generate_fallback_predictions(insight_summary):
    top_files = insight_summary.get("top_risky_files", [])
    fallback_analysis = []

    # 🔥 Case 1: No risky files
    if not top_files:
        for i in range(3):
            fallback_analysis.append({
                "priority_rank": i + 1,
                "title": f"[Fallback] General codebase improvement #{i+1}",
                "what_is_wrong": "Potential maintainability or structural issues",
                "how_serious": "Medium",
                "where_exactly": {
                    "primary_folder": "entire_repo",
                    "affected_files": []
                },
                "why_it_matters": "Unstructured code can lead to bugs and slow development",
                "if_ignored": "Technical debt accumulation",
                "what_to_fix_first": "Improve modularity, add tests, refactor large files",
                "estimated_effort": "Medium",
                "confidence": 0.6
            })

    # 🔥 Case 2: Risky files exist (THIS WAS MISSING)
    else:
        for i, file in enumerate(top_files[:3]):
            fallback_analysis.append({
                "priority_rank": i + 1,
                "title": f"[Fallback] Refactor {file.get('file_path', 'file')}",
                "what_is_wrong": "High complexity or risk detected",
                "how_serious": "High",
                "where_exactly": {
                    "primary_folder": file.get("folder_path", "unknown"),
                    "affected_files": [file.get("file_path")]
                },
                "why_it_matters": "High-risk files increase bugs and maintenance cost",
                "if_ignored": "Technical debt increases",
                "what_to_fix_first": "Refactor and simplify logic",
                "estimated_effort": "Medium",
                "confidence": 0.7
            })

    return {
        "executive_summary": {
            "overall_health_score": 0,
            "primary_risk_driver": "Fallback analysis",
            "risk_trend": "unknown"
        },
        "ai_analysis": fallback_analysis
    }
def build_prompt(summary):
    """Build the prompt for LLM prediction."""
    return f"""
Repository Metrics:
{json.dumps(summary.get("repo_metrics", {}), indent=2)}

Structure Metrics:
{json.dumps(summary.get("structure_metrics", {}), indent=2)}

Top Risky Files:
{json.dumps(summary.get("top_risky_files", []), indent=2)}

Security Hotspots:
{json.dumps(summary.get("security_hotspots", []), indent=2)}

Risk Concentration Ratio:
{summary.get("risk_concentration_ratio", 0)}

Generate structured AI explanation with MINIMUM 3 insights MUST be provided.
Return only valid JSON.
"""


def generate_llm_repo_predictions(insight_summary):
    """Generate LLM-based predictions with robust fallback, quality validation, and exponential backoff."""
    
    # DEBUG: Check if top_risky_files is populated
    print("🔍 DEBUG - TOP_RISKY_FILES:", insight_summary.get("top_risky_files"))
    logger.debug(f"Top risky files: {insight_summary.get('top_risky_files')}")
    
    # Check if API key available
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set. Using fallback prediction generation.")
        parsed = generate_fallback_predictions(insight_summary)
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
            logger.debug(f"Attempting LLM prediction (attempt {attempt + 1}/{GROQ_RETRIES})")
            
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
            
            # Enforce minimum predictions with quality validation
            parsed = ensure_min_predictions(parsed, insight_summary)
            
            logger.info(f"Successfully retrieved {len(parsed.get('ai_analysis', []))} predictions from LLM")
            
            metadata = {
                "model": result.get("model"),
                "usage": result.get("usage"),
                "finish_reason": result["choices"][0].get("finish_reason"),
                "source": "llm"
            }
            
            return parsed, metadata
        
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.error(f"LLM prediction attempt {attempt + 1} failed: {type(e).__name__}: {str(e)}")
            
            if attempt == GROQ_RETRIES - 1:
                # Last attempt failed, use fallback
                logger.warning("All LLM attempts exhausted. Activating offline fallback.")
                parsed = generate_fallback_predictions(insight_summary)
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
    parsed = generate_fallback_predictions(insight_summary)
    metadata = {"model": "fallback", "source": "offline_fallback"}
    return parsed, metadata
