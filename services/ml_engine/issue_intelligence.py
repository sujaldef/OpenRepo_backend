import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from services.ml_engine.embedding_service import get_embedding


class IssueIntelligence:

    def __init__(self):

        # Predefined semantic prototypes (safe static vectors)
        self.category_prototypes = {
            "Security Risk": get_embedding("code injection vulnerability authentication token exposure"),
            "Performance Risk": get_embedding("slow inefficient loop blocking memory heavy computation"),
            "Maintainability Debt": get_embedding("complex hard to read nested long function technical debt"),
            "Debug Leakage": get_embedding("console log debug statement production data leak"),
            "Error Handling Risk": get_embedding("unhandled exception crash failure missing validation"),
        }

    def enrich_issue(self, issue: dict, code_context: str, metrics: dict = None) -> dict:

        try:
            embedding = get_embedding(code_context)
        except Exception:
            embedding = np.zeros(768)

        # -----------------------------
        # 1️⃣ Semantic Classification
        # -----------------------------
        category_scores = {}

        for category, proto_vec in self.category_prototypes.items():
            sim = cosine_similarity(
                [embedding],
                [proto_vec]
            )[0][0]
            category_scores[category] = float(sim)

        semantic_category = max(category_scores, key=category_scores.get)
        semantic_strength = category_scores[semantic_category]

        # -----------------------------
        # 2️⃣ Contextual Risk Adjustment
        # -----------------------------
        contextual_boost = 0.0

        if metrics:
            if metrics.get("cyclomatic_complexity", 0) > 10:
                contextual_boost += 0.1
            if metrics.get("has_tests", 1) == 0:
                contextual_boost += 0.1
            if metrics.get("security_issue_count", 0) > 0:
                contextual_boost += 0.15

        exploit_probability = min(1.0, semantic_strength + contextual_boost)

        # -----------------------------
        # 3️⃣ Dynamic Root Cause
        # -----------------------------
        root_cause = self._infer_root_cause(issue, code_context)

        # -----------------------------
        # 4️⃣ Smart Fix Suggestion
        # -----------------------------
        fix_suggestion = self._generate_fix(issue, semantic_category)

        issue["analysis"] = {
            "semantic_category": semantic_category,
            "semantic_strength": round(semantic_strength, 4),
            "exploit_probability": round(exploit_probability, 4),
            "root_cause": root_cause,
            "recommended_action": fix_suggestion,
            "confidence": round(min(1.0, semantic_strength + 0.2), 4)
        }

        return issue

    def _infer_root_cause(self, issue, context):

        if "eval" in context.lower():
            return "Dynamic code execution detected."
        if "console" in context.lower():
            return "Debug statement present in runtime path."
        if "except:" in context:
            return "Broad exception handler suppressing error specificity."
        if "password" in context.lower() or "token" in context.lower():
            return "Sensitive data handling detected."

        return "Pattern indicates structural weakness or maintainability concern."

    def _generate_fix(self, issue, category):

        if category == "Security Risk":
            return "Replace unsafe operations with validated and sanitized alternatives."
        if category == "Performance Risk":
            return "Refactor heavy loops or optimize algorithmic structure."
        if category == "Maintainability Debt":
            return "Break into smaller modular functions and improve readability."
        if category == "Debug Leakage":
            return "Remove debug statements or replace with structured logging."
        if category == "Error Handling Risk":
            return "Add proper validation and specific exception handling."

        return "Refactor the affected logic following best practices."