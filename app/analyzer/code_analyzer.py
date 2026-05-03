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
        is_acc = context.get("is_accumulator", False)

        # Loop variables are fine
        if is_loop:
            return 10

        # Parameter naming penalty
        if is_param and len(name) <= 2:
            score -= 3

        # Generic bad names
        if name in self.GENERIC_BAD:
            score -= 2

        # Short names
        if len(name) <= 2:
            score -= 1 if is_acc else -3

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
    # LOAD CODE
    # ======================================================
    def load_code(self, code: str):
        self.source_code = code
        self.tree = ast.parse(code)

    # ======================================================
    # FUNCTION SOURCE
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
    # VARIABLE ANALYSIS
    # ======================================================
    def analyze_variables(self, func):
        analyzer = VariableAnalyzer()

        func_size = self.get_metrics(func)["length"]

        # Params
        param_names = {arg.arg for arg in func.args.args} if hasattr(func, "args") else set()

        # Loop vars
        loop_vars = set()
        for node in ast.walk(func):
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                loop_vars.add(node.target.id)

        # Accumulators
        accumulators = set()

        for node in ast.walk(func):
            if isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name):
                    accumulators.add(node.target.id)

            elif isinstance(node, ast.Assign):
                if isinstance(node.value, ast.BinOp):
                    if isinstance(node.targets[0], ast.Name):
                        left = node.value.left
                        if isinstance(left, ast.Name):
                            if left.id == node.targets[0].id:
                                accumulators.add(left.id)

        results_map = {}

        for node in ast.walk(func):
            if isinstance(node, ast.Name):

                context = {
                    "function_size": func_size,
                    "is_param": node.id in param_names,
                    "is_loop": node.id in loop_vars,
                    "is_accumulator": node.id in accumulators
                }

                score = analyzer.score_variable(node.id, context)

                if score < 7:
                    if node.id not in results_map or score < results_map[node.id]["score"]:
                        results_map[node.id] = {
                            "name": node.id,
                            "score": score,
                            "reason": self._explain_variable(score, node.id)
                        }

        return list(results_map.values())

    # ======================================================
    # EXPLANATION
    # ======================================================
    def _explain_variable(self, score, name=None, context=None):
        if score <= 3:
            return f"'{name}' is unclear and too generic. It does not describe its purpose."
        elif score <= 6:
            return f"'{name}' is somewhat descriptive but still weak. Consider making intent clearer."
        else:
            return f"'{name}' is acceptable but could still be improved."

    # ======================================================
    # UNUSED VARIABLES
    # ======================================================
    def get_unused_variables(self, func):
        assigned = set()
        used = set()
        params = {arg.arg for arg in func.args.args}

        for node in ast.walk(func):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                assigned.add(node.id)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)

        unused = assigned - used - params

        builtin_names = {
            "print", "len", "range", "str", "int", "float",
            "list", "dict", "set", "tuple", "input"
        }

        return [v for v in unused if v not in builtin_names]

    # ======================================================
    # LOCAL VARIABLES
    # ======================================================
    def get_local_variable_count(self, func):
        return len({n.id for n in ast.walk(func) if isinstance(n, ast.Name)})

    # ======================================================
    # SUGGESTIONS
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
                issues.append({"type": "Too many local variables", "severity": "Medium"})

            for i in issues:
                i["suggestion"] = self.get_suggestion(i["type"], func.name)

            score = 10
            for i in issues:
                if i["severity"] == "Critical":
                    score -= 5
                elif i["severity"] == "High":
                    score -= 3
                else:
                    score -= 2

            score = max(score, 0)

            func_code = self.get_function_source(func)
            ai_review = self.ai.generate_review(func_code)

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
    # FILTERS (RESTORED FIX)
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