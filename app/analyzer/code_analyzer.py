from app.analyzer.complexity_analyzer import ComplexityAnalyzer
from app.analyzer.variable_analyzer import VariableAnalyzer
from app.ai.ai_engine import AIEngine

import ast
import hashlib
from typing import Optional


# ======================================================
# SEVERITY CONSTANTS
# ======================================================
class Severity:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# ======================================================
# THRESHOLDS
# ======================================================
class Thresholds:
    FUNC_LENGTH_WARN = 20
    FUNC_LENGTH_MEDIUM = 10

    ARGS_MAX = 4

    COMPLEXITY_HIGH = 10
    COMPLEXITY_CRITICAL = 20

    NESTING_HIGH = 3
    NESTING_CRITICAL = 5

    LOCAL_VARS_MAX = 10

    SCORE_WEIGHT_LOW = 0.5
    SCORE_WEIGHT_MEDIUM = 1.0
    SCORE_WEIGHT_HIGH = 1.5
    SCORE_WEIGHT_CRITICAL = 2.5


# ======================================================
# MAIN ANALYZER
# ======================================================
class CodeAnalyzer:
    ENGINE_VERSION = "2.1.0"

    def __init__(self, file_path: str = ""):
        self.file_path = file_path

        self.tree: Optional[ast.AST] = None
        self.source_code = ""

        self._parse_error: Optional[str] = None

        # analyzers
        self.variable_analyzer = VariableAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()

        # lazy AI
        self._ai: Optional[AIEngine] = None

        # cache
        self._cache: Optional[list[dict]] = None
        self._cache_hash: Optional[str] = None

    # ======================================================
    # LAZY AI
    # ======================================================
    @property
    def ai(self) -> AIEngine:
        if self._ai is None:
            self._ai = AIEngine()
        return self._ai

    # ======================================================
    # HASH
    # ======================================================
    def _hash(self, code: str) -> str:
        return hashlib.md5(code.encode()).hexdigest()

    # ======================================================
    # LOAD CODE
    # ======================================================
    def load_code(self, code: str) -> bool:
        self._parse_error = None

        try:
            self.source_code = code
            self.tree = ast.parse(code)

            code_hash = self._hash(code)

            if code_hash != self._cache_hash:
                self.invalidate_cache()
                self._cache_hash = code_hash

            return True

        except SyntaxError as exc:
            self.tree = None
            self.source_code = ""
            self.invalidate_cache()

            self._parse_error = str(exc)

            return False

    # ======================================================
    # PARSE ERROR
    # ======================================================
    @property
    def parse_error(self) -> Optional[str]:
        return self._parse_error

    # ======================================================
    # FUNCTION SOURCE
    # ======================================================
    def get_function_source(
        self,
        func: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> str:
        try:
            lines = self.source_code.splitlines()

            start = func.lineno - 1
            end = getattr(func, "end_lineno", func.lineno)

            return "\n".join(lines[start:end])

        except Exception:
            return ""

    # ======================================================
    # FUNCTION EXTRACTION
    # ======================================================
    def get_functions(self) -> list:
        if not self.tree:
            return []

        return [
            node
            for node in ast.walk(self.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    # ======================================================
    # CLASS EXTRACTION
    # ======================================================
    def get_classes(self) -> list[ast.ClassDef]:
        if not self.tree:
            return []

        return [
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.ClassDef)
        ]

    # ======================================================
    # COMPLEXITY
    # ======================================================
    def get_complexity(self, func) -> int:
        try:
            return self.complexity_analyzer.analyze(func)
        except Exception:
            return 0

    # ======================================================
    # METRICS
    # ======================================================
    def get_metrics(self, func) -> dict:
        length = (
            getattr(func, "end_lineno", func.lineno)
            - func.lineno
            + 1
        )

        args = len(func.args.args)

        has_defaults = len(func.args.defaults) > 0

        is_async = isinstance(func, ast.AsyncFunctionDef)

        has_docstring = (
            bool(ast.get_docstring(func))
        )

        return {
            "length": length,
            "args": args,
            "has_defaults": has_defaults,
            "is_async": is_async,
            "has_docstring": has_docstring,
            "line_start": func.lineno,
            "line_end": getattr(func, "end_lineno", func.lineno),
        }

    # ======================================================
    # NESTING DEPTH
    # ======================================================
    def get_max_nesting(
        self,
        node: ast.AST,
        depth: int = 0
    ) -> int:

        nesting_nodes = (
            ast.If,
            ast.For,
            ast.While,
            ast.With,
            ast.Try,
            ast.ExceptHandler,
        )

        max_depth = depth

        for child in ast.iter_child_nodes(node):

            child_depth = (
                depth + 1
                if isinstance(child, nesting_nodes)
                else depth
            )

            max_depth = max(
                max_depth,
                self.get_max_nesting(child, child_depth)
            )

        return max_depth

    # ======================================================
    # UNUSED VARIABLES
    # ======================================================
    def get_unused_variables(self, func) -> list[str]:

        assigned = set()
        used = set()

        params = {
            arg.arg
            for arg in func.args.args
        }

        for node in ast.walk(func):

            if isinstance(node, ast.Name):

                if isinstance(node.ctx, ast.Store):
                    assigned.add(node.id)

                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        return sorted(list(assigned - used - params))

    # ======================================================
    # LOCAL VARIABLE COUNT
    # ======================================================
    def get_local_variable_count(self, func) -> int:

        return len({
            node.id
            for node in ast.walk(func)
            if (
                isinstance(node, ast.Name)
                and isinstance(node.ctx, ast.Store)
            )
        })

    # ======================================================
    # RETURN COUNT
    # ======================================================
    def get_return_count(self, func) -> int:

        return sum(
            1
            for node in ast.walk(func)
            if isinstance(node, ast.Return)
        )

    # ======================================================
    # COMMENT DENSITY
    # ======================================================
    def get_comment_density(self, func) -> float:

        try:
            lines = self.get_function_source(func).splitlines()

            total = len(lines)

            comments = sum(
                1
                for line in lines
                if line.strip().startswith("#")
            )

            return round(comments / total, 2) if total else 0.0

        except Exception:
            return 0.0

    # ======================================================
    # BUILD ISSUES
    # ======================================================
    def _build_issues(
        self,
        metrics: dict,
        complexity: int,
        nesting: int,
        variables: list,
        unused: list,
        local_count: int,
        return_count: int,
    ) -> list[dict]:

        t = Thresholds

        issues = []

        # function length
        if metrics["length"] > t.FUNC_LENGTH_WARN:

            issues.append({
                "type": "Too long",
                "severity": Severity.HIGH,
                "detail": (
                    f"{metrics['length']} lines "
                    f"(warn > {t.FUNC_LENGTH_WARN})"
                ),
            })

        elif metrics["length"] > t.FUNC_LENGTH_MEDIUM:

            issues.append({
                "type": "Slightly long",
                "severity": Severity.MEDIUM,
                "detail": f"{metrics['length']} lines",
            })

        # arguments
        if metrics["args"] > t.ARGS_MAX:

            issues.append({
                "type": "Too many args",
                "severity": Severity.MEDIUM,
                "detail": (
                    f"{metrics['args']} args "
                    f"(max {t.ARGS_MAX})"
                ),
            })

        # complexity
        if complexity > t.COMPLEXITY_CRITICAL:

            issues.append({
                "type": "Critically complex",
                "severity": Severity.CRITICAL,
                "detail": f"Cyclomatic complexity = {complexity}",
            })

        elif complexity > t.COMPLEXITY_HIGH:

            issues.append({
                "type": "Too complex",
                "severity": Severity.HIGH,
                "detail": f"Cyclomatic complexity = {complexity}",
            })

        # nesting
        if nesting >= t.NESTING_CRITICAL:

            issues.append({
                "type": "Critical nesting",
                "severity": Severity.CRITICAL,
                "detail": f"Max depth = {nesting}",
            })

        elif nesting >= t.NESTING_HIGH:

            issues.append({
                "type": "Deep nesting",
                "severity": Severity.HIGH,
                "detail": f"Max depth = {nesting}",
            })

        # variables
        if variables:

            issues.append({
                "type": "Poor variable names",
                "severity": Severity.MEDIUM,
                "detail": f"{len(variables)} flagged variable(s)",
            })

        # unused vars
        if unused:

            issues.append({
                "type": "Unused variables",
                "severity": Severity.MEDIUM,
                "detail": str(unused),
            })

        # local vars
        if local_count > t.LOCAL_VARS_MAX:

            issues.append({
                "type": "Too many locals",
                "severity": Severity.MEDIUM,
                "detail": f"{local_count} local variables",
            })

        # returns
        if return_count > 5:

            issues.append({
                "type": "Too many returns",
                "severity": Severity.LOW,
                "detail": f"{return_count} return statements",
            })

        # docstring
        if not metrics["has_docstring"]:

            issues.append({
                "type": "No docstring",
                "severity": Severity.LOW,
                "detail": "Function has no docstring",
            })

        return issues

    # ======================================================
    # SCORE
    # ======================================================
    def _compute_score(self, issues: list[dict]) -> int:

        t = Thresholds

        weight_map = {
            Severity.LOW: t.SCORE_WEIGHT_LOW,
            Severity.MEDIUM: t.SCORE_WEIGHT_MEDIUM,
            Severity.HIGH: t.SCORE_WEIGHT_HIGH,
            Severity.CRITICAL: t.SCORE_WEIGHT_CRITICAL,
        }

        penalty = sum(
            weight_map.get(issue["severity"], 1.0)
            for issue in issues
        )

        return max(0, round(10 - penalty))

    # ======================================================
    # INSIGHT ENGINE
    # ======================================================
    def generate_insight(
        self,
        metrics: dict,
        nesting: int,
        issues: list[dict],
    ) -> str:

        tags = []

        if metrics["length"] > Thresholds.FUNC_LENGTH_WARN:
            tags.append("Large function")

        if metrics["args"] > Thresholds.ARGS_MAX:
            tags.append("High coupling")

        if nesting >= Thresholds.NESTING_HIGH:
            tags.append("Deep nesting")

        critical = [
            issue
            for issue in issues
            if issue["severity"] == Severity.CRITICAL
        ]

        if critical:
            tags.append(f"{len(critical)} critical issue(s)")

        elif len(issues) >= 3:
            tags.append("Multiple issues")

        if not metrics["has_docstring"]:
            tags.append("Undocumented")

        if metrics["is_async"]:
            tags.append("Async")

        return " | ".join(tags) if tags else "Clean structure"

    # ======================================================
    # CACHE LAYER
    # ======================================================
    def _run(self) -> list[dict]:

        if self._cache is not None:
            return self._cache

        self._cache = self._analyze_internal()

        return self._cache

    # ======================================================
    # INTERNAL ANALYSIS
    # ======================================================
    def _analyze_internal(self) -> list[dict]:

        results = []

        for func in self.get_functions():

            complexity = self.get_complexity(func)

            metrics = self.get_metrics(func)

            nesting = self.get_max_nesting(func)

            return_count = self.get_return_count(func)

            comment_density = self.get_comment_density(func)

            variables = self.variable_analyzer.analyze(
                func=func,
                function_size=metrics["length"],
            )

            unused = self.get_unused_variables(func)

            local_count = self.get_local_variable_count(func)

            issues = self._build_issues(
                metrics=metrics,
                complexity=complexity,
                nesting=nesting,
                variables=variables,
                unused=unused,
                local_count=local_count,
                return_count=return_count,
            )

            score = self._compute_score(issues)

            # AI review
            try:

                ai_review = self.ai.generate_review({
                    "code": self.get_function_source(func),
                    "issues": issues,
                    "metrics": metrics,
                    "complexity": complexity,
                    "nesting": nesting,
                })

            except Exception:
                ai_review = "AI unavailable"

            results.append({
                "name": func.name,
                "metrics": metrics,
                "complexity": complexity,
                "nesting": nesting,
                "return_count": return_count,
                "comment_density": comment_density,
                "variables": variables,
                "unused": unused,
                "issues": issues,
                "score": score,
                "ai_review": ai_review,
                "insight": self.generate_insight(
                    metrics,
                    nesting,
                    issues,
                ),
                "engine_version": self.ENGINE_VERSION,
            })

        return results

    # ======================================================
    # MODULE STATS
    # ======================================================
    def module_stats(self) -> dict:

        results = self._run()

        all_scores = [
            result["score"]
            for result in results
        ]

        all_issues = [
            issue
            for result in results
            for issue in result["issues"]
        ]

        severity_counts = {
            Severity.LOW: 0,
            Severity.MEDIUM: 0,
            Severity.HIGH: 0,
            Severity.CRITICAL: 0,
        }

        for issue in all_issues:

            severity = issue.get(
                "severity",
                Severity.LOW
            )

            severity_counts[severity] += 1

        return {
            "total_functions": len(results),
            "total_classes": len(self.get_classes()),
            "average_score": (
                round(sum(all_scores) / len(all_scores), 2)
                if all_scores else 10.0
            ),
            "total_issues": len(all_issues),
            "severity_counts": severity_counts,
            "undocumented": sum(
                1
                for result in results
                if not result["metrics"]["has_docstring"]
            ),
            "async_functions": sum(
                1
                for result in results
                if result["metrics"]["is_async"]
            ),
        }

    # ======================================================
    # PUBLIC API
    # ======================================================
    def full_analysis(self) -> list[dict]:
        return self._run()

    def get_worst_functions(
        self,
        limit: int = 5
    ) -> list[dict]:

        return sorted(
            self._run(),
            key=lambda x: x["score"]
        )[:limit]

    def get_best_functions(
        self,
        limit: int = 5
    ) -> list[dict]:

        return sorted(
            self._run(),
            key=lambda x: x["score"],
            reverse=True,
        )[:limit]

    def get_problematic_functions(self) -> list[dict]:

        return [
            func
            for func in self._run()
            if func["issues"]
        ]

    def get_critical_functions(self) -> list[dict]:

        return [
            func
            for func in self._run()
            if any(
                issue["severity"] == Severity.CRITICAL
                for issue in func["issues"]
            )
        ]

    def get_undocumented_functions(self) -> list[dict]:

        return [
            func
            for func in self._run()
            if not func["metrics"]["has_docstring"]
        ]

    def get_function_by_name(
        self,
        name: str
    ) -> Optional[dict]:

        return next(
            (
                func
                for func in self._run()
                if func["name"] == name
            ),
            None,
        )

    def invalidate_cache(self) -> None:

        self._cache = None
        self._cache_hash = None