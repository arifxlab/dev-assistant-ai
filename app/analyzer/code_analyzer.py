from app.analyzer.complexity_analyzer import ComplexityAnalyzer
from app.analyzer.variable_analyzer import VariableAnalyzer
from app.ai.ai_engine import AIEngine

import ast
import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional


# ======================================================
# SEVERITY CONSTANTS
# ======================================================
class Severity:
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"


# ======================================================
# THRESHOLDS  — centralised so they're easy to tune
# ======================================================
class Thresholds:
    FUNC_LENGTH_WARN     = 20
    FUNC_LENGTH_MEDIUM   = 10
    ARGS_MAX             = 4
    COMPLEXITY_HIGH      = 10
    COMPLEXITY_CRITICAL  = 20
    NESTING_HIGH         = 3
    NESTING_CRITICAL     = 5
    LOCAL_VARS_MAX       = 10
    SCORE_WEIGHT_LOW      = 0.5
    SCORE_WEIGHT_MEDIUM   = 1.0
    SCORE_WEIGHT_HIGH     = 1.5
    SCORE_WEIGHT_CRITICAL = 2.5


# ======================================================
# MAIN ANALYZER
# ======================================================
class CodeAnalyzer:
    ENGINE_VERSION = "2.0.0"

    def __init__(self, file_path: str = "", lazy_ai: bool = True):
        self.file_path = file_path
        self.tree: Optional[ast.AST] = None
        self.source_code = ""
        self._parse_error: Optional[str] = None

        # engines
        self._ai: Optional[AIEngine] = None
        self._lazy_ai = lazy_ai                     # defer AI init until needed
        self.variable_analyzer = VariableAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()

        # cache
        self._cache: Optional[list[dict]] = None
        self._cache_hash: Optional[str] = None

    # ======================================================
    # LAZY AI PROPERTY  (fixes silent startup cost)
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
        """
        Parse the source code and reset cache if it changed.
        Returns True on success, False on syntax error.
        """
        self._parse_error = None

        try:
            self.source_code = code
            self.tree = ast.parse(code)

            code_hash = self._hash(code)
            if code_hash != self._cache_hash:
                self._cache = None
                self._cache_hash = code_hash

            return True

        except SyntaxError as exc:
            self._parse_error = str(exc)
            self.tree = None
            self.source_code = ""
            self._cache = None
            return False

    # ======================================================
    # PARSE ERROR
    # ======================================================
    @property
    def parse_error(self) -> Optional[str]:
        """Returns the last SyntaxError message, or None."""
        return self._parse_error

    # ======================================================
    # FUNCTION SOURCE
    # ======================================================
    def get_function_source(self, func: ast.FunctionDef) -> str:
        try:
            lines = self.source_code.splitlines()
            start = func.lineno - 1
            end   = getattr(func, "end_lineno", func.lineno)
            return "\n".join(lines[start:end])
        except Exception:
            return ""

    # ======================================================
    # FUNCTION EXTRACTION  (includes async functions)
    # ======================================================
    def get_functions(self) -> list[ast.FunctionDef]:
        if not self.tree:
            return []

        return [
            node for node in ast.walk(self.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    # ======================================================
    # CLASS EXTRACTION  (new feature)
    # ======================================================
    def get_classes(self) -> list[ast.ClassDef]:
        if not self.tree:
            return []

        return [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.ClassDef)
        ]

    # ======================================================
    # COMPLEXITY
    # ======================================================
    def get_complexity(self, func: ast.FunctionDef) -> int:
        try:
            return self.complexity_analyzer.analyze(func)
        except Exception:
            return 0

    # ======================================================
    # METRICS
    # ======================================================
    def get_metrics(self, func: ast.FunctionDef) -> dict:
        length = (
            getattr(func, "end_lineno", func.lineno) - func.lineno + 1
        )
        args         = len(func.args.args)
        has_defaults = len(func.args.defaults) > 0
        is_async     = isinstance(func, ast.AsyncFunctionDef)
        has_docstring = (
            isinstance(func.body[0], ast.Expr)
            and isinstance(func.body[0].value, ast.Constant)
            and isinstance(func.body[0].value.value, str)
        ) if func.body else False

        return {
            "length":       length,
            "args":         args,
            "has_defaults": has_defaults,
            "is_async":     is_async,
            "has_docstring": has_docstring,
            "line_start":   func.lineno,
            "line_end":     getattr(func, "end_lineno", func.lineno),
        }

    # ======================================================
    # NESTING DEPTH
    # ======================================================
    def get_max_nesting(self, node: ast.AST, depth: int = 0) -> int:
        NESTING_NODES = (ast.If, ast.For, ast.While, ast.With,
                         ast.Try, ast.ExceptHandler)

        max_depth = depth

        for child in ast.iter_child_nodes(node):
            child_depth = depth + 1 if isinstance(child, NESTING_NODES) else depth
            max_depth = max(max_depth, self.get_max_nesting(child, child_depth))

        return max_depth

    # ======================================================
    # UNUSED VARIABLES  (fixed: only counts Store contexts)
    # ======================================================
    def get_unused_variables(self, func: ast.FunctionDef) -> list[str]:
        assigned: set[str] = set()
        used: set[str]     = set()
        params             = {a.arg for a in func.args.args}

        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        return list(assigned - used - params)

    # ======================================================
    # LOCAL VARIABLE COUNT  (fixed: Store-only, no reads)
    # ======================================================
    def get_local_variable_count(self, func: ast.FunctionDef) -> int:
        return len({
            node.id
            for node in ast.walk(func)
            if isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Store)
        })

    # ======================================================
    # RETURN COUNT  (new feature)
    # ======================================================
    def get_return_count(self, func: ast.FunctionDef) -> int:
        return sum(
            1 for node in ast.walk(func)
            if isinstance(node, ast.Return)
        )

    # ======================================================
    # LINES OF CODE vs COMMENT RATIO  (new feature)
    # ======================================================
    def get_comment_density(self, func: ast.FunctionDef) -> float:
        """Returns ratio of comment lines to total lines (0.0–1.0)."""
        try:
            lines = self.get_function_source(func).splitlines()
            total   = len(lines)
            comments = sum(1 for l in lines if l.strip().startswith("#"))
            return round(comments / total, 2) if total else 0.0
        except Exception:
            return 0.0

    # ======================================================
    # ISSUE BUILDER  (severity-aware, fixes Critical gap)
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

        # ── Length ─────────────────────────────────────
        if metrics["length"] > t.FUNC_LENGTH_WARN:
            issues.append({
                "type":     "Too long",
                "severity": Severity.HIGH,
                "detail":   f"{metrics['length']} lines (warn > {t.FUNC_LENGTH_WARN})",
            })
        elif metrics["length"] > t.FUNC_LENGTH_MEDIUM:
            issues.append({
                "type":     "Slightly long",
                "severity": Severity.MEDIUM,
                "detail":   f"{metrics['length']} lines",
            })

        # ── Args ───────────────────────────────────────
        if metrics["args"] > t.ARGS_MAX:
            issues.append({
                "type":     "Too many args",
                "severity": Severity.MEDIUM,
                "detail":   f"{metrics['args']} args (max {t.ARGS_MAX})",
            })

        # ── Complexity ─────────────────────────────────
        if complexity > t.COMPLEXITY_CRITICAL:
            issues.append({
                "type":     "Critically complex",
                "severity": Severity.CRITICAL,
                "detail":   f"Cyclomatic complexity = {complexity}",
            })
        elif complexity > t.COMPLEXITY_HIGH:
            issues.append({
                "type":     "Too complex",
                "severity": Severity.HIGH,
                "detail":   f"Cyclomatic complexity = {complexity}",
            })

        # ── Nesting ────────────────────────────────────
        if nesting >= t.NESTING_CRITICAL:
            issues.append({
                "type":     "Critical nesting",
                "severity": Severity.CRITICAL,
                "detail":   f"Max depth = {nesting}",
            })
        elif nesting >= t.NESTING_HIGH:
            issues.append({
                "type":     "Deep nesting",
                "severity": Severity.HIGH,
                "detail":   f"Max depth = {nesting}",
            })

        # ── Variable quality ───────────────────────────
        if variables:
            issues.append({
                "type":     "Poor variable names",
                "severity": Severity.MEDIUM,
                "detail":   f"{len(variables)} flagged variable(s)",
            })

        # ── Unused variables ───────────────────────────
        if unused:
            issues.append({
                "type":     "Unused variables",
                "severity": Severity.MEDIUM,
                "detail":   f"{unused}",
            })

        # ── Local variable count ────────────────────────
        if local_count > t.LOCAL_VARS_MAX:
            issues.append({
                "type":     "Too many locals",
                "severity": Severity.MEDIUM,
                "detail":   f"{local_count} local variables",
            })

        # ── Multiple returns ───────────────────────────
        if return_count > 5:
            issues.append({
                "type":     "Too many returns",
                "severity": Severity.LOW,
                "detail":   f"{return_count} return statements",
            })

        # ── Missing docstring ──────────────────────────
        if not metrics["has_docstring"]:
            issues.append({
                "type":     "No docstring",
                "severity": Severity.LOW,
                "detail":   "Function has no docstring",
            })

        return issues

    # ======================================================
    # SEVERITY-WEIGHTED SCORE  (fixes blunt formula)
    # ======================================================
    def _compute_score(self, issues: list[dict]) -> int:
        t = Thresholds
        weight_map = {
            Severity.LOW:      t.SCORE_WEIGHT_LOW,
            Severity.MEDIUM:   t.SCORE_WEIGHT_MEDIUM,
            Severity.HIGH:     t.SCORE_WEIGHT_HIGH,
            Severity.CRITICAL: t.SCORE_WEIGHT_CRITICAL,
        }
        penalty = sum(weight_map.get(i["severity"], 1.0) for i in issues)
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

        critical = [i for i in issues if i["severity"] == Severity.CRITICAL]
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
            complexity   = self.get_complexity(func)
            metrics      = self.get_metrics(func)
            nesting      = self.get_max_nesting(func)
            return_count = self.get_return_count(func)
            comment_density = self.get_comment_density(func)

            variables = self.variable_analyzer.analyze(
                func=func,
                function_size=metrics["length"],
            )

            unused      = self.get_unused_variables(func)
            local_count = self.get_local_variable_count(func)

            issues = self._build_issues(
                metrics, complexity, nesting,
                variables, unused, local_count, return_count,
            )

            score = self._compute_score(issues)

            # AI review
            try:
                ai_review = self.ai.generate_review({
                    "code":        self.get_function_source(func),
                    "issues":      issues,
                    "metrics":     metrics,
                    "complexity":  complexity,
                    "nesting":     nesting,
                })
            except Exception:
                ai_review = "AI unavailable"

            results.append({
                "name":             func.name,
                "metrics":          metrics,
                "complexity":       complexity,
                "nesting":          nesting,
                "return_count":     return_count,
                "comment_density":  comment_density,
                "variables":        variables,
                "unused":           unused,
                "issues":           issues,
                "score":            score,
                "ai_review":        ai_review,
                "insight":          self.generate_insight(metrics, nesting, issues),
                "engine_version":   self.ENGINE_VERSION,
            })

        return results

    # ======================================================
    # MODULE-LEVEL STATS  (new feature)
    # ======================================================
    def module_stats(self) -> dict:
        """
        Aggregate stats across the entire module.
        """
        results     = self._run()
        all_scores  = [r["score"] for r in results]
        all_issues  = [i for r in results for i in r["issues"]]

        severity_counts = {
            Severity.LOW:      0,
            Severity.MEDIUM:   0,
            Severity.HIGH:     0,
            Severity.CRITICAL: 0,
        }
        for issue in all_issues:
            sev = issue.get("severity", Severity.LOW)
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "total_functions":   len(results),
            "total_classes":     len(self.get_classes()),
            "average_score":     round(sum(all_scores) / len(all_scores), 2) if all_scores else 10.0,
            "total_issues":      len(all_issues),
            "severity_counts":   severity_counts,
            "undocumented":      sum(1 for r in results if not r["metrics"]["has_docstring"]),
            "async_functions":   sum(1 for r in results if r["metrics"]["is_async"]),
        }

    # ======================================================
    # PUBLIC API
    # ======================================================
    def full_analysis(self) -> list[dict]:
        """Return full analysis for all functions."""
        return self._run()

    def get_worst_functions(self, limit: int = 5) -> list[dict]:
        """Return the N lowest-scoring functions."""
        return sorted(self._run(), key=lambda x: x["score"])[:limit]

    def get_best_functions(self, limit: int = 5) -> list[dict]:
        """Return the N highest-scoring functions."""
        return sorted(self._run(), key=lambda x: x["score"], reverse=True)[:limit]

    def get_problematic_functions(self) -> list[dict]:
        """Return all functions with at least one issue."""
        return [f for f in self._run() if f["issues"]]

    def get_critical_functions(self) -> list[dict]:
        """Return functions with at least one Critical severity issue."""
        return [
            f for f in self._run()
            if any(i["severity"] == Severity.CRITICAL for i in f["issues"])
        ]

    def get_undocumented_functions(self) -> list[dict]:
        """Return all functions missing a docstring."""
        return [
            f for f in self._run()
            if not f["metrics"]["has_docstring"]
        ]

    def get_function_by_name(self, name: str) -> Optional[dict]:
        """Look up a single function's analysis by name."""
        return next(
            (f for f in self._run() if f["name"] == name),
            None,
        )

    def invalidate_cache(self) -> None:
        """Force re-analysis on the next call."""
        self._cache = None
        self._cache_hash = None