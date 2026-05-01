from app.analyzer.complexity_analyzer import ComplexityAnalyzer
from app.ai.ai_engine import AIEngine
import ast


# ======================================================
# VARIABLE ANALYZER (SCORING ENGINE)
# ======================================================
class VariableAnalyzer:
    LOOP_NAMES = {"i", "j", "k", "idx", "index"}
    GENERIC_BAD = {"temp", "data", "value", "result", "var"}

    def score_variable(self, name, context):
        score = 10

        func_size = context["function_size"]
        is_param = context.get("is_param", False)
        is_loop = context.get("is_loop", False)

        # Loop variables are OK
        if name in self.LOOP_NAMES or is_loop:
            return 10

        # Parameters stricter
        if is_param and len(name) <= 2:
            score -= 3

        # Generic weak names
        if name in self.GENERIC_BAD:
            score -= 2

        # Very short names
        if len(name) <= 2:
            score -= 3

        # Large function penalty
        if func_size > 20 and len(name) <= 3:
            score -= 2

        return max(score, 0)


# ======================================================
# MAIN ANALYZER
# ======================================================
class CodeAnalyzer:
    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.tree = None
        self.source_code = ""
        self.ai = AIEngine()

    # ======================================================
    # LOAD CODE (IN MEMORY)
    # ======================================================
    def load_code(self, code: str):
        self.source_code = code
        self.tree = ast.parse(code)

    # ======================================================
    # GET FUNCTION SOURCE
    # ======================================================
    def get_function_source(self, func):
        lines = self.source_code.splitlines()
        start = func.lineno - 1
        end = getattr(func, "end_lineno", func.lineno)
        return "\n".join(lines[start:end])

    # ======================================================
    # FUNCTION EXTRACTION
    # ======================================================
    def get_functions(self):
        return [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
        ]

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
    # VARIABLE ANALYSIS (NEW SYSTEM)
    # ======================================================
    def analyze_variables(self, func):
        analyzer = VariableAnalyzer()

        results = []
        func_size = self.get_metrics(func)["length"]

        seen = set()

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                if node.id in seen:
                    continue
                seen.add(node.id)

                context = {
                    "function_size": func_size,
                    "is_param": isinstance(node.ctx, ast.Param),
                    "is_loop": False
                }

                score = analyzer.score_variable(node.id, context)

                if score < 7:
                    results.append({
                        "name": node.id,
                        "score": score,
                        "reason": self._explain_variable(score)
                    })

        return results

    def _explain_variable(self, score):
        if score <= 3:
            return "Very weak / unclear naming"
        elif score <= 6:
            return "Weak naming, consider improving"
        else:
            return "Acceptable"

    # ======================================================
    # UNUSED VARIABLES (FIXED)
    # ======================================================
    def get_unused_variables(self, func):
        assigned = set()
        used = set()
        params = set()

        # parameters
        for arg in func.args.args:
            params.add(arg.arg)

        for node in ast.walk(func):

            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                assigned.add(node.id)

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)

        unused = assigned - used
        unused = unused - params

        builtin_names = {
            "print", "len", "range", "str", "int", "float",
            "list", "dict", "set", "tuple", "input"
        }

        unused = [v for v in unused if v not in builtin_names]

        return list(unused)

    # ======================================================
    # LOCAL VARIABLE COUNT
    # ======================================================
    def get_local_variable_count(self, func):
        return len({n.id for n in ast.walk(func) if isinstance(n, ast.Name)})

    # ======================================================
    # RULE SUGGESTIONS
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
    # INSIGHT ENGINE
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
    # MAIN ANALYSIS
    # ======================================================
    def full_analysis(self):
        results = []

        for func in self.get_functions():

            complexity = self.get_complexity(func)
            metrics = self.get_metrics(func)
            nesting = self.get_max_nesting(func)

            variables = self.analyze_variables(func)
            unused_vars = self.get_unused_variables(func)
            local_var_count = self.get_local_variable_count(func)

            issues = []

            # RULES
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

            if variables:
                issues.append({"type": "Bad variables", "severity": "Medium"})

            if unused_vars:
                issues.append({"type": "Unused variables", "severity": "Medium"})

            if local_var_count > 10:
                issues.append({
                    "type": "Too many local variables",
                    "severity": "Medium"
                })

            # suggestions
            for i in issues:
                i["suggestion"] = self.get_suggestion(i["type"], func.name)

            # score
            score = 10
            for i in issues:
                if i["severity"] == "Critical":
                    score -= 5
                elif i["severity"] == "High":
                    score -= 3
                else:
                    score -= 2

            score = max(score, 0)

            # AI review
            func_code = self.get_function_source(func)
            ai_review = self.ai.generate_review(func_code)

            # insight
            insight = self.generate_insight(metrics, nesting, issues)

            results.append({
                "name": func.name,
                "length": metrics["length"],
                "args": metrics["args"],
                "complexity": complexity,
                "nesting": nesting,
                "variables": {
                    "quality": variables,
                    "unused": unused_vars,
                    "count": local_var_count
                },
                "issues": issues,
                "score": score,
                "ai_insight": insight,
                "ai_review": ai_review
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