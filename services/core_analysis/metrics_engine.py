import ast
import os
import re


def compute_metrics(file_path: str):
    metrics = {
        "loc": 0,
        "function_count": 0,
        "avg_function_length": 0.0,
        "max_function_length": 0,
        "cyclomatic_complexity": 1,
        "max_nesting_depth": 0,
        "total_issue_count": 0,
        "security_issue_count": 0,
        "duplication_ratio": 0.0,
        "dependency_risk_score": 0.0,
        "has_tests": 0
    }

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        metrics["loc"] = len(code.splitlines())
    except:
        return metrics

    ext = os.path.splitext(file_path)[1].lower()

    # =========================
    # PYTHON METRICS
    # =========================
    if ext == ".py":
        try:
            tree = ast.parse(code)
        except:
            return metrics

        functions = []
        max_depth = 0
        complexity = 1

        for node in ast.walk(tree):

            if isinstance(node, (
                ast.If, ast.For, ast.While,
                ast.Try, ast.With,
                ast.BoolOp, ast.ExceptHandler
            )):
                complexity += 1

            if isinstance(node, ast.FunctionDef):
                functions.append(node)

            depth = calculate_nesting_depth(node)
            max_depth = max(max_depth, depth)

        function_lengths = []

        for fn in functions:
            start = fn.lineno
            end = max(
                getattr(n, "lineno", start)
                for n in ast.walk(fn)
            )
            function_lengths.append(end - start + 1)

        metrics["function_count"] = len(functions)

        if function_lengths:
            metrics["avg_function_length"] = sum(function_lengths) / len(function_lengths)
            metrics["max_function_length"] = max(function_lengths)

        metrics["cyclomatic_complexity"] = complexity
        metrics["max_nesting_depth"] = max_depth

    # =========================
    # JAVASCRIPT / TYPESCRIPT
    # =========================
    elif ext in [".js", ".jsx", ".ts", ".tsx"]:

        function_patterns = [
            r'\bfunction\b',
            r'=>',
            r'export\s+function'
        ]

        decision_patterns = [
            r'\bif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bfor\s*\(',
            r'\bwhile\s*\(',
            r'\bswitch\s*\('
        ]

        function_count = sum(len(re.findall(p, code)) for p in function_patterns)
        complexity = 1 + sum(len(re.findall(p, code)) for p in decision_patterns)

        metrics["function_count"] = function_count
        metrics["cyclomatic_complexity"] = complexity

    return metrics


def calculate_nesting_depth(node, current_depth=0):
    max_depth = current_depth

    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
            depth = calculate_nesting_depth(child, current_depth + 1)
        else:
            depth = calculate_nesting_depth(child, current_depth)

        max_depth = max(max_depth, depth)

    return max_depth