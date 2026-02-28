import ast
import re
import os
from services.ml_engine.issue_intelligence import IssueIntelligence


def analyze_file_defects(file_path: str) -> dict:
    issues = []
    intelligence = IssueIntelligence()

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
            lines = code.splitlines()
    except Exception:
        issues.append({
            "type": "IO Error",
            "severity": "error",
            "message": "Could not read file",
            "line": 1
        })
        return {"issues": issues}

    ext = os.path.splitext(file_path)[1].lower()

    # ───────────────────────────────────────────────
    #          PYTHON DEFECT ANALYSIS
    # ───────────────────────────────────────────────
    if ext == ".py":
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "type": "Syntax Error",
                "severity": "error",
                "message": f"Syntax error: {str(e)}",
                "line": getattr(e, "lineno", 1)
            })
            return {"issues": issues}
        except Exception as e:
            issues.append({
                "type": "Parse Error",
                "severity": "error",
                "message": f"Failed to parse AST: {str(e)}",
                "line": 1
            })
            return {"issues": issues}

        for node in ast.walk(tree):

            # ── Security ───────────────────────────────────────
            # eval() usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "eval":
                    issues.append({
                        "type": "Security",
                        "severity": "error",
                        "message": "Use of eval() is extremely dangerous",
                        "line": node.lineno
                    })

            # Hardcoded secrets (very basic but useful heuristic)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(kw in name_lower for kw in [
                            "password", "passwd", "pwd", "secret", "api_key",
                            "apikey", "token", "authkey", "private_key", "access_key"
                        ]):
                            issues.append({
                                "type": "Security",
                                "severity": "warning",
                                "message": f"Possible hardcoded credential: '{target.id}'",
                                "line": node.lineno
                            })

            # ── Code Smells / Maintainability ──────────────────
            # Too many parameters
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args) + len(node.args.kwonlyargs)
                if param_count > 7:
                    issues.append({
                        "type": "Code Smell",
                        "severity": "warning",
                        "message": f"Function '{node.name}' has too many parameters ({param_count})",
                        "line": node.lineno
                    })

                # Long function (body line count — rough heuristic)
                if len(node.body) > 60:
                    issues.append({
                        "type": "Code Smell",
                        "severity": "warning",
                        "message": f"Function '{node.name}' is too long ({len(node.body)} statements)",
                        "line": node.lineno
                    })

            # Large class (many methods)
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                if method_count > 25:
                    issues.append({
                        "type": "Code Smell",
                        "severity": "warning",
                        "message": f"Class '{node.name}' is very large ({method_count} methods)",
                        "line": node.lineno
                    })

            # Bare except (very dangerous)
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append({
                        "type": "Code Smell",
                        "severity": "error",
                        "message": "Bare 'except:' clause — catches everything including KeyboardInterrupt",
                        "line": node.lineno
                    })

            # Note: Deep nesting detection was incomplete in original
            # You would typically need a NodeVisitor + parent tracking for accurate nesting depth

    # ───────────────────────────────────────────────
    #     JAVASCRIPT / TYPESCRIPT / JSX / TSX ANALYSIS
    # ───────────────────────────────────────────────
    if ext in [".js", ".jsx", ".ts", ".tsx"]:

        # Debug statements
        console_pattern = re.compile(r'console\s*\.\s*(log|debug|info|warn|error)\s*\(', re.IGNORECASE)
        for match in console_pattern.finditer(code):
            line_no = code[:match.start()].count('\n') + 1
            issues.append({
                "type": "Debug Code",
                "severity": "warning",
                "message": "Console statement found — remove before production",
                "line": line_no
            })

        # eval() — dangerous
        eval_pattern = re.compile(r'\beval\s*\(', re.IGNORECASE)
        for match in eval_pattern.finditer(code):
            line_no = code[:match.start()].count('\n') + 1
            issues.append({
                "type": "Security",
                "severity": "error",
                "message": "Use of eval() detected — high security risk",
                "line": line_no
            })

        # Very basic (and approximate) function & complexity estimation
        function_keywords = [r'\bfunction\b', r'=>', r'export\s+function']
        decision_keywords = [
            r'\bif\s*\(', r'\belse\s+if\s*\(', r'\bfor\s*\(',
            r'\bwhile\s*\(', r'\bswitch\s*\('
        ]

        function_count = sum(len(re.findall(pat, code)) for pat in function_keywords)
        complexity = 1 + sum(len(re.findall(pat, code)) for pat in decision_keywords)

        if function_count > 15:
            issues.append({
                "type": "Code Smell",
                "severity": "warning",
                "message": f"File has many functions/declarations (~{function_count})",
                "line": 1
            })

        if complexity > 25:
            issues.append({
                "type": "Complexity",
                "severity": "warning",
                "message": f"High approximate cyclomatic complexity (~{complexity})",
                "line": 1
            })

    # Enrich issues with ML signals
    enriched_issues = []

    for issue in issues:
        line_number = issue.get("line", 1)
        snippet = lines[line_number - 1] if 0 < line_number <= len(lines) else ""
        enriched_issue = intelligence.enrich_issue(issue, snippet)
        enriched_issues.append(enriched_issue)

    return {"issues": enriched_issues}