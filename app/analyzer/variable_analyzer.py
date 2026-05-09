import ast
from dataclasses import dataclass, field
from typing import Optional


# ======================================================
# DATA CLASSES
# ======================================================
@dataclass
class VariableReport:
    name: str
    score: int
    reason: str
    line: int
    category: str                        # param | loop | accumulator | local
    suggestions: list[str] = field(default_factory=list)


# ======================================================
# VARIABLE ANALYZER
# ======================================================
class VariableAnalyzer:

    # Generic bad names that carry no semantic meaning
    GENERIC_BAD = {"temp", "data", "value", "result", "var", "obj",
                   "item", "thing", "stuff", "info", "val", "x", "y",
                   "z", "foo", "bar", "baz"}

    # Conventionally accepted single/double-letter names
    CONVENTIONAL_OK = {"i", "j", "k", "e", "f", "n", "x", "y", "id",
                       "ok", "fp", "fd", "db", "io"}

    # ======================================================
    # MAIN VARIABLE ANALYSIS
    # ======================================================
    def analyze(self, func: ast.FunctionDef, function_size: int) -> list[dict]:
        """
        Analyze all variables in a function and return reports
        for those with a score below the threshold (7).
        """
        param_names  = {a.arg for a in func.args.args}
        loop_vars    = self._collect_loop_vars(func)
        accumulators = self._collect_accumulators(func)
        line_map     = self._build_line_map(func)

        results: dict[str, VariableReport] = {}

        for node in ast.walk(func):
            if not isinstance(node, ast.Name):
                continue

            name = node.id

            # Skip builtins / dunder names
            if name.startswith("__") or name in dir(__builtins__):
                continue

            category = self._categorize(
                name, param_names, loop_vars, accumulators
            )

            context = {
                "function_size": function_size,
                "is_param":       name in param_names,
                "is_loop":        name in loop_vars,
                "is_accumulator": name in accumulators,
                "category":       category,
            }

            score = self.score_variable(name, context)

            if score < 7:
                line = line_map.get(name, getattr(node, "lineno", 0))

                report = VariableReport(
                    name        = name,
                    score       = score,
                    reason      = self.explain(score, name, category),
                    line        = line,
                    category    = category,
                    suggestions = self.suggest(name, category),
                )

                # Keep the worst (lowest) score per variable name
                if name not in results or score < results[name].score:
                    results[name] = report

        return [vars(r) for r in results.values()]

    # ======================================================
    # LOOP VARIABLE COLLECTION  (fixes tuple-unpack bug)
    # ======================================================
    def _collect_loop_vars(self, func: ast.FunctionDef) -> set[str]:
        loop_vars: set[str] = set()

        for node in ast.walk(func):
            if isinstance(node, ast.For):
                loop_vars.update(self._extract_names(node.target))

        return loop_vars

    def _extract_names(self, node: ast.expr) -> list[str]:
        """Recursively extract names from assignment targets (handles tuples)."""
        if isinstance(node, ast.Name):
            return [node.id]
        if isinstance(node, (ast.Tuple, ast.List)):
            names = []
            for elt in node.elts:
                names.extend(self._extract_names(elt))
            return names
        return []

    # ======================================================
    # ACCUMULATOR COLLECTION
    # ======================================================
    def _collect_accumulators(self, func: ast.FunctionDef) -> set[str]:
        accumulators: set[str] = set()

        for node in ast.walk(func):
            if isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name):
                    accumulators.add(node.target.id)

        return accumulators

    # ======================================================
    # LINE MAP  — first appearance of each name
    # ======================================================
    def _build_line_map(self, func: ast.FunctionDef) -> dict[str, int]:
        line_map: dict[str, int] = {}

        for node in ast.walk(func):
            if isinstance(node, ast.Name) and hasattr(node, "lineno"):
                if node.id not in line_map:
                    line_map[node.id] = node.lineno

        return line_map

    # ======================================================
    # CATEGORY
    # ======================================================
    def _categorize(
        self,
        name: str,
        params: set[str],
        loop_vars: set[str],
        accumulators: set[str],
    ) -> str:
        if name in params:       return "param"
        if name in loop_vars:    return "loop"
        if name in accumulators: return "accumulator"
        return "local"

    # ======================================================
    # VARIABLE SCORING  (severity-aware, fixed inversion)
    # ======================================================
    def score_variable(self, name: str, context: dict) -> int:
        """
        Returns a quality score 0–10.
        10 = excellent,  < 7 = flagged for review.
        """
        is_loop        = context.get("is_loop", False)
        is_param       = context.get("is_param", False)
        is_accumulator = context.get("is_accumulator", False)
        func_size      = context.get("function_size", 0)

        # Conventionally accepted short names are always fine
        if name in self.CONVENTIONAL_OK:
            return 10

        # Loop variables are contextually clear
        if is_loop:
            return 10

        score = 10

        # ── Generic / meaningless names ──────────────────
        if name in self.GENERIC_BAD:
            score -= 4

        # ── Very short names (1–2 chars) ─────────────────
        if len(name) == 1:
            # Single-letter accumulators (n, s, c) are common & OK
            penalty = 1 if is_accumulator else 4
            score  -= penalty

        elif len(name) == 2:
            penalty = 1 if is_accumulator else 3
            score  -= penalty

        # ── Short params carry extra weight ──────────────
        if is_param and len(name) <= 2:
            score -= 2          # on top of the length penalty above

        # ── Extra penalty in larger functions ────────────
        if func_size > 20 and len(name) <= 3:
            score -= 2

        # ── Underscore-only or all-digit names ───────────
        if name.replace("_", "") == "" or name.isdigit():
            score -= 5

        return max(score, 0)

    # ======================================================
    # EXPLANATION ENGINE  (corrected branch ordering)
    # ======================================================
    def explain(self, score: int, name: str, category: str) -> str:
        cat_label = {
            "param":       "parameter",
            "loop":        "loop variable",
            "accumulator": "accumulator",
            "local":       "local variable",
        }.get(category, "variable")

        if score <= 2:
            return f"'{name}' ({cat_label}) is too vague to be meaningful"
        if score <= 4:
            return f"'{name}' ({cat_label}) is unclear — consider a descriptive name"
        if score <= 6:
            return f"'{name}' ({cat_label}) is weak — a more specific name would help"
        return f"'{name}' ({cat_label}) is acceptable but could be clearer"

    # ======================================================
    # SUGGESTION ENGINE  (new feature)
    # ======================================================
    def suggest(self, name: str, category: str) -> list[str]:
        tips: list[str] = []

        if name in self.GENERIC_BAD:
            tips.append(
                f"Replace '{name}' with a name that describes "
                "what it holds (e.g. 'user_count', 'total_price')"
            )

        if len(name) <= 2 and category == "param":
            tips.append(
                "Short parameter names hurt readability at call sites — "
                "use a full word (e.g. 'index' instead of 'i')"
            )

        if len(name) <= 2 and category == "local":
            tips.append(
                "Single/double-letter locals are hard to search for; "
                "use at least 3 descriptive characters"
            )

        if not tips:
            tips.append("Consider a more descriptive name")

        return tips

    # ======================================================
    # SUMMARY REPORT  (new feature)
    # ======================================================
    def summary(self, func: ast.FunctionDef, function_size: int) -> dict:
        """
        High-level summary of variable quality for the function.
        """
        issues = self.analyze(func, function_size)

        scores = [v["score"] for v in issues] or [10]
        avg    = round(sum(scores) / len(scores), 2)

        severity_counts = {"critical": 0, "warning": 0, "info": 0}
        for v in issues:
            s = v["score"]
            if s <= 2:   severity_counts["critical"] += 1
            elif s <= 4: severity_counts["warning"]  += 1
            else:        severity_counts["info"]     += 1

        return {
            "total_flagged":    len(issues),
            "average_score":    avg,
            "severity_counts":  severity_counts,
            "issues":           issues,
        }