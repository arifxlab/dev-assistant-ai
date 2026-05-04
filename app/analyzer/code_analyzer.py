from app.analyzer.complexity_analyzer import ComplexityAnalyzer
from app.ai.ai_engine import AIEngine
import ast
import hashlib


# ======================================================
# VARIABLE ANALYZER (SCORING ENGINE)
# ======================================================
class VariableAnalyzer:
    LOOP_NAMES = {"i", "j", "k", "idx", "index"}
    GENERIC_BAD = {"temp", "data", "value", "result", "var"}

    def score_variable(self, name, context):
        score = 10

        func_size = context.get("function_size", 0)
        is_param = context.get("is_param", False)
        is_loop = context.get("is_loop", False)
        is_acc = context.get("is_accumulator", False)

        if is_loop:
            return 10

        if is_param and len(name) <= 2:
            score -= 3

        if name in self.GENERIC_BAD:
            score -= 2

        if len(name) <= 2:
            score -= 1 if is_acc else 3

        if func_size > 20 and len(name) <= 3:
            score -= 2

        return max(score, 0)


# ======================================================
# MAIN ANALYZER
# ======================================================
class CodeAnalyzer:
    ENGINE_VERSION = "1.0.0"

    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.tree = None
        self.source_code = ""
        self.ai = AIEngine()

        # 🔥 CACHE SYSTEM (NEW)
        self._cache = None
        self._cache_hash = None

    # ======================================================
    # HASH
    # ======================================================
    def _hash(self, code: str):
        return hashlib.md5(code.encode()).hexdigest()

    # ======================================================
    # LOAD CODE
    # ======================================================
    def load_code(self, code: str):
        try:
            self.source_code = code
            self.tree = ast.parse(code)

            # invalidate cache if code changed
            code_hash = self._hash(code)
            if code_hash != self._cache_hash:
                self._cache = None
                self._cache_hash = code_hash

        except Exception:
            self.tree = None
            self.source_code = ""
            self._cache = None

    # ======================================================
    # FUNCTION SOURCE
    # ======================================================
    def get_function_source(self, func):
        try:
            lines = self.source_code.splitlines()
            start = func.lineno - 1
            end = getattr(func, "end_lineno", func.lineno)
            return "\n".join(lines[start:end])
        except Exception:
            return ""

    # ======================================================
    # FUNCTIONS
    # ======================================================
    def get_functions(self):
        if not self.tree:
            return []

        return [
            n for n in ast.walk(self.tree)
            if isinstance(n, ast.FunctionDef)
        ]

    # ======================================================
    # COMPLEXITY
    # ======================================================
    def get_complexity(self, func):
        try:
            return ComplexityAnalyzer().analyze(func)
        except Exception:
            return 0

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
    # VARIABLE ANALYSIS (CLEAN + FAST)
    # ======================================================
    def analyze_variables(self, func):
        analyzer = VariableAnalyzer()

        func_size = self.get_metrics(func)["length"]

        param_names = {a.arg for a in func.args.args}

        loop_vars = set()
        accumulators = set()

        for node in ast.walk(func):

            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                loop_vars.add(node.target.id)

            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                accumulators.add(node.target.id)

        results = {}

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                name = node.id

                context = {
                    "function_size": func_size,
                    "is_param": name in param_names,
                    "is_loop": name in loop_vars,
                    "is_accumulator": name in accumulators
                }

                score = analyzer.score_variable(name, context)

                if score < 7:
                    if name not in results or score < results[name]["score"]:
                        results[name] = {
                            "name": name,
                            "score": score,
                            "reason": self._explain(score, name)
                        }

        return list(results.values())

    def _explain(self, score, name):
        if score <= 3:
            return f"{name} is unclear"
        if score <= 6:
            return f"{name} is weak"
        return f"{name} is acceptable"

    # ======================================================
    # UNUSED VARIABLES
    # ======================================================
    def get_unused_variables(self, func):
        assigned = set()
        used = set()
        params = {a.arg for a in func.args.args}

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        unused = assigned - used - params

        return list(unused)

    # ======================================================
    # LOCAL VARIABLES
    # ======================================================
    def get_local_variable_count(self, func):
        return len({n.id for n in ast.walk(func) if isinstance(n, ast.Name)})

    # ======================================================
    # INSIGHT
    # ======================================================
    def generate_insight(self, metrics, nesting, issues):
        out = []

        if metrics["length"] > 20:
            out.append("Large function")
        if metrics["args"] > 4:
            out.append("High coupling")
        if nesting >= 3:
            out.append("Deep nesting")
        if len(issues) >= 3:
            out.append("Multiple issues")

        return " | ".join(out) if out else "Clean structure"

    # ======================================================
    # CACHE LAYER (🔥 IMPORTANT)
    # ======================================================
    def _run(self):
        if self._cache is not None:
            return self._cache

        self._cache = self._analyze_internal()
        return self._cache

    # ======================================================
    # INTERNAL ANALYSIS
    # ======================================================
    def _analyze_internal(self):
        results = []

        for func in self.get_functions():

            complexity = self.get_complexity(func)
            metrics = self.get_metrics(func)
            nesting = self.get_max_nesting(func)

            variables = self.analyze_variables(func)
            unused = self.get_unused_variables(func)
            local_count = self.get_local_variable_count(func)

            issues = []

            if metrics["length"] > 10:
                issues.append({"type": "Too long", "severity": "Medium"})
            if metrics["args"] > 4:
                issues.append({"type": "Too many args", "severity": "Medium"})
            if complexity > 10:
                issues.append({"type": "Too complex", "severity": "High"})
            if nesting >= 3:
                issues.append({"type": "Deep nesting", "severity": "High"})
            if variables:
                issues.append({"type": "Bad variables", "severity": "Medium"})
            if unused:
                issues.append({"type": "Unused vars", "severity": "Medium"})

            score = max(0, 10 - len(issues) * 2)

            try:
                ai_review = self.ai.generate_review({
                    "code": self.get_function_source(func),
                    "issues": issues,
                    "metrics": metrics,
                    "complexity": complexity,
                    "nesting": nesting
                })
            except Exception:
                ai_review = "AI unavailable"

            results.append({
                "name": func.name,
                "metrics": metrics,
                "complexity": complexity,
                "nesting": nesting,
                "variables": variables,
                "unused": unused,
                "issues": issues,
                "score": score,
                "ai_review": ai_review,
                "insight": self.generate_insight(metrics, nesting, issues),
                "engine_version": self.ENGINE_VERSION
            })

        return results

    # ======================================================
    # PUBLIC API
    # ======================================================
    def full_analysis(self):
        return self._run()

    def get_worst_functions(self):
        return sorted(self._run(), key=lambda x: x["score"])

    def get_problematic_functions(self):
        return [f for f in self._run() if f["issues"]]

    def get_critical_functions(self):
        return [
            f for f in self._run()
            if any(i["severity"] == "Critical" for i in f["issues"])
        ]