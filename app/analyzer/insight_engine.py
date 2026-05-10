from app.analyzer.code_analyzer import Thresholds, Severity


class InsightEngine:

    @staticmethod
    def generate(metrics, nesting, issues):

        tags = []

        if metrics["length"] > Thresholds.FUNC_LENGTH_WARN:
            tags.append("Large function")

        if metrics["args"] > Thresholds.ARGS_MAX:
            tags.append("High coupling")

        if nesting >= Thresholds.NESTING_HIGH:
            tags.append("Deep nesting")

        critical = [
            issue for issue in issues
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