from app.analyzer.complexity_analyzer import ComplexityAnalyzer
from app.ai.ai_engine import AIEngine
import ast


class CodeAnalyzer:
    """
    ======================================================
    LEVEL 4 READY ANALYZER (FINAL MERGED VERSION)
    ======================================================
    - AST parsing
    - Complexity analysis
    - Nesting detection
    - Variable analysis
    - Rule-based issues
    - AI suggestions
    - AI insight
    - REAL AI review (Ollama)
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None
        self.ai = AIEngine()  # 🔥 AI initialized

    # ======================================================
    # LOAD SOURCE CODE
    # ======================================================
    def load_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.tree = ast.parse(f.read())

    # ======================================================
    # FUNCTION EXTRACTION
    # ======================================================
    def get_functions(self):
        return [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
        ]

    # ======================================================
    # EXTRACT FUNCTION CODE (FOR AI)
    # ======================================================
    def get_function_code(self, func):
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start = func.lineno - 1
        end = getattr(func, "end_lineno", func.lineno)

        return "".join(lines[start:end])

    # ======================================================
    # COMPLEXITY
    # ======================================================
    def get_complexity(self, func):
        return ComplexityAnalyzer().analyze(func)

    # ======================================================
    # METRICS
    # ======================================================
    def get_metrics(self, func):
        length = getattr(func, "end_lineno", func.lineno) - func.lineno + 1
        args = len(func.args.args)

        return {"length": length, "args": args}

    # ======================================================
    # NESTING
    # ======================================================
    def get_max_nesting(self, node, depth=0):
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                max_depth = max(max_depth, self.get_max_nesting(child, depth + 1))
            else:
                max_depth = max(max_depth, self.get_max_nesting(child, depth))

        return max_depth

    # ======================================================
    # VARIABLE ANALYSIS
    # ======================================================
    def get_bad_variable_names(self, func):
        weak_names = {"x", "y", "z", "temp", "data", "val"}
        bad = []

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                if node.id in weak_names or len(node.id) == 1:
                    bad.append(node.id)

        return list(set(bad))

    def get_unused_variables(self, func):
        assigned = set()
        used = set()

        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned.add(target.id)
            elif isinstance(node, ast.Name):
                used.add(node.id)

        return list(assigned - used)

    def get_local_variable_count(self, func):
        vars_found = set()

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                vars_found.add(node.id)

        return len(vars_found)

    # ======================================================
    # AI SUGGESTIONS (RULE-BASED)
    # ======================================================
    def get_suggestion(self, issue, func_name):
        return {
            "Too long": f"Refactor '{func_name}' into smaller functions.",
            "Too many arguments": f"Reduce parameters in '{func_name}'.",
            "Too complex": f"Simplify logic in '{func_name}'.",
            "Deep nesting": f"Flatten logic in '{func_name}'.",
            "God Function": f"Split '{func_name}' into multiple functions.",
            "Bad variables": f"Use meaningful variable names in '{func_name}'.",
            "Unused variables": f"Remove unused variables in '{func_name}'."
        }.get(issue, "No suggestion available.")

    # ======================================================
    # AI INSIGHT (SMART SUMMARY)
    # ======================================================
    def generate_insight(self, metrics, nesting, issues):
        insights = []

        if metrics["length"] > 20:
            insights.append("Function is too large.")

        if metrics["args"] > 4:
            insights.append("Too many parameters increase coupling.")

        if nesting >= 3:
            insights.append("Deep nesting increases complexity.")

        if len(issues) >= 3:
            insights.append("Multiple design issues detected.")

        return " ".join(insights) if insights else "Structure looks good."

    # ======================================================
    # MAIN ANALYSIS ENGINE
    # ======================================================
    def full_analysis(self):
        results = []

        for func in self.get_functions():

            complexity = self.get_complexity(func)
            metrics = self.get_metrics(func)
            nesting = self.get_max_nesting(func)

            bad_vars = self.get_bad_variable_names(func)
            unused_vars = self.get_unused_variables(func)
            local_var_count = self.get_local_variable_count(func)

            issues = []

            # ---------------- RULES ----------------
            if metrics["length"] > 10:
                issues.append({"type": "Too long", "severity": "Medium"})

            if metrics["args"] > 4:
                issues.append({"type": "Too many arguments", "severity": "Medium"})

            if complexity > 10:
                issues.append({"type": "Too complex", "severity": "High"})

            if nesting >= 3:
                issues.append({"type": "Deep nesting", "severity": "High"})

            if metrics["length"] > 30 or complexity > 15:
                issues.append({"type": "God Function", "severity": "Critical"})

            if bad_vars:
                issues.append({"type": "Bad variables", "severity": "Medium"})

            if unused_vars:
                issues.append({"type": "Unused variables", "severity": "Medium"})

            # add suggestions
            for i in issues:
                i["suggestion"] = self.get_suggestion(i["type"], func.name)

            # ---------------- SCORE ----------------
            score = 10
            for i in issues:
                if i["severity"] == "Critical":
                    score -= 5
                elif i["severity"] == "High":
                    score -= 3
                elif i["severity"] == "Medium":
                    score -= 2

            if nesting >= 3:
                score -= 2

            score = max(score, 0)

            # ---------------- AI REVIEW (🔥 MAIN FEATURE) ----------------
            func_code = self.get_function_code(func)
            ai_review = self.ai.generate_review(func_code)

            # ---------------- INSIGHT ----------------
            insight = self.generate_insight(metrics, nesting, issues)

            results.append({
                "name": func.name,
                "length": metrics["length"],
                "args": metrics["args"],
                "complexity": complexity,
                "nesting": nesting,
                "variables": {
                    "bad": bad_vars,
                    "unused": unused_vars,
                    "count": local_var_count
                },
                "issues": issues,
                "score": score,
                "ai_insight": insight,
                "ai_review": ai_review   # 🔥 REAL AI OUTPUT
            })

        return results

    # ======================================================
    # FILTERS
    # ======================================================
    def get_worst_functions(self):
        return sorted(self.full_analysis(), key=lambda x: x["score"])

    def get_problematic_functions(self):
        return [f for f in self.full_analysis() if f["issues"]]

    def get_critical_functions(self):
        return [
            f for f in self.full_analysis()
            if any(i["severity"] == "Critical" for i in f["issues"])
        ]