from app.analyzer.complexity_analyzer import ComplexityAnalyzer
import ast


class CodeAnalyzer:
    """
    ======================================================
    LEVEL 3++ CODE ANALYSIS ENGINE (MERGED VERSION)
    ======================================================

    Features:
    - AST parsing
    - Complexity analysis
    - Nesting detection
    - Variable analysis (bad names, unused, count)
    - AI-style suggestions
    - AI insight engine
    - Smart scoring system
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None

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
    # COMPLEXITY ANALYSIS
    # ======================================================
    def get_complexity(self, func):
        return ComplexityAnalyzer().analyze(func)

    # ======================================================
    # BASIC METRICS
    # ======================================================
    def get_metrics(self, func):
        length = getattr(func, "end_lineno", func.lineno) - func.lineno + 1
        args = len(func.args.args)

        return {
            "length": length,
            "args": args
        }

    # ======================================================
    # NESTING DETECTOR
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
    # VARIABLE ANALYSIS (MERGED FEATURE)
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
    # AI SUGGESTION ENGINE
    # ======================================================
    def get_suggestion(self, issue, func_name, value=None):
        return {
            "Too long": f"Refactor '{func_name}' into smaller functions.",
            "Too many arguments": f"Reduce parameters in '{func_name}' using class/dict.",
            "Too complex": f"Simplify logic in '{func_name}' by reducing nesting.",
            "Deep nesting": f"Flatten logic in '{func_name}' using early returns.",
            "God Function": f"Split '{func_name}' into multiple functions.",
            "Bad variables": f"Use meaningful variable names in '{func_name}'.",
            "Unused variables": f"Remove unused variables in '{func_name}'."
        }.get(issue, "No suggestion available.")

    # ======================================================
    # AI INSIGHT ENGINE
    # ======================================================
    def generate_insight(self, func_name, issues, metrics, nesting):
        insights = []

        if metrics["length"] > 20:
            insights.append("Function is doing too many things.")

        if metrics["args"] > 4:
            insights.append("Too many parameters increases coupling.")

        if nesting >= 3:
            insights.append("Deep nesting increases cognitive complexity.")

        if len(issues) >= 3:
            insights.append("Multiple design issues detected — refactor needed.")

        return " ".join(insights) if insights else "Code structure is clean."

    # ======================================================
    # MAIN ANALYSIS ENGINE
    # ======================================================
    def full_analysis(self):
        results = []

        for func in self.get_functions():

            complexity = self.get_complexity(func)
            metrics = self.get_metrics(func)
            nesting = self.get_max_nesting(func)

            # -------------------------
            # VARIABLE ANALYSIS (MERGED)
            # -------------------------
            bad_vars = self.get_bad_variable_names(func)
            unused_vars = self.get_unused_variables(func)
            local_var_count = self.get_local_variable_count(func)

            issues = []

            # =========================
            # RULE ENGINE
            # =========================

            if metrics["length"] > 10:
                issues.append({
                    "type": "Too long",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Too long", func.name)
                })

            if metrics["args"] > 4:
                issues.append({
                    "type": "Too many arguments",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Too many arguments", func.name)
                })

            if complexity > 10:
                issues.append({
                    "type": "Too complex",
                    "severity": "High",
                    "suggestion": self.get_suggestion("Too complex", func.name)
                })

            if nesting >= 3:
                issues.append({
                    "type": "Deep nesting",
                    "severity": "High",
                    "suggestion": self.get_suggestion("Deep nesting", func.name)
                })

            if metrics["length"] > 30 or complexity > 15:
                issues.append({
                    "type": "God Function",
                    "severity": "Critical",
                    "suggestion": self.get_suggestion("God Function", func.name)
                })

            if bad_vars:
                issues.append({
                    "type": "Bad variables",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Bad variables", func.name)
                })

            if unused_vars:
                issues.append({
                    "type": "Unused variables",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Unused variables", func.name)
                })

            if local_var_count > 10:
                issues.append({
                    "type": "Too many local variables",
                    "severity": "Medium",
                    "suggestion": "Break function into smaller logic blocks."
                })

            # =========================
            # SCORING ENGINE
            # =========================
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

            # =========================
            # AI INSIGHT
            # =========================
            insight = self.generate_insight(
                func.name,
                issues,
                metrics,
                nesting
            )

            # =========================
            # FINAL RESULT
            # =========================
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
                "ai_insight": insight
            })

        return results

    # ======================================================
    # FILTER FUNCTIONS
    # ======================================================
    def get_worst_functions(self):
        return sorted(self.full_analysis(), key=lambda x: x["score"])

    def get_problematic_functions(self):
        return [f for f in self.full_analysis() if f["issues"]]

    def get_critical_functions(self):
        return [
            {
                "name": f["name"],
                "score": f["score"],
                "issues": f["issues"]
            }
            for f in self.full_analysis()
            if any(i["severity"] == "Critical" for i in f["issues"])
        ]