from app.analyzer.code_analyzer import Severity, Thresholds


class IssueEngine:

    @staticmethod
    def build(
        metrics,
        complexity,
        nesting,
        variables,
        unused,
        local_count,
        return_count,
    ):

        t = Thresholds

        issues = []

        # =============================================
        # FUNCTION LENGTH
        # =============================================
        if metrics["length"] > t.FUNC_LENGTH_WARN:
            issues.append({
                "type": "Too long",
                "severity": Severity.HIGH,
                "detail": f"{metrics['length']} lines",
            })

        elif metrics["length"] > t.FUNC_LENGTH_MEDIUM:
            issues.append({
                "type": "Slightly long",
                "severity": Severity.MEDIUM,
                "detail": f"{metrics['length']} lines",
            })

        # =============================================
        # ARGUMENT COUNT
        # =============================================
        if metrics["args"] > t.ARGS_MAX:
            issues.append({
                "type": "Too many args",
                "severity": Severity.MEDIUM,
                "detail": f"{metrics['args']} args",
            })

        # =============================================
        # COMPLEXITY
        # =============================================
        if complexity > t.COMPLEXITY_CRITICAL:
            issues.append({
                "type": "Critically complex",
                "severity": Severity.CRITICAL,
                "detail": f"Complexity = {complexity}",
            })

        elif complexity > t.COMPLEXITY_HIGH:
            issues.append({
                "type": "Too complex",
                "severity": Severity.HIGH,
                "detail": f"Complexity = {complexity}",
            })

        # =============================================
        # NESTING
        # =============================================
        if nesting >= t.NESTING_CRITICAL:
            issues.append({
                "type": "Critical nesting",
                "severity": Severity.CRITICAL,
                "detail": f"Nesting = {nesting}",
            })

        elif nesting >= t.NESTING_HIGH:
            issues.append({
                "type": "Deep nesting",
                "severity": Severity.HIGH,
                "detail": f"Nesting = {nesting}",
            })

        # =============================================
        # VARIABLES
        # =============================================
        if variables:
            issues.append({
                "type": "Poor variable names",
                "severity": Severity.MEDIUM,
                "detail": f"{len(variables)} flagged variable(s)",
            })

        # =============================================
        # UNUSED VARIABLES
        # =============================================
        if unused:
            issues.append({
                "type": "Unused variables",
                "severity": Severity.MEDIUM,
                "detail": f"{unused}",
            })

        # =============================================
        # LOCAL VARIABLES
        # =============================================
        if local_count > t.LOCAL_VARS_MAX:
            issues.append({
                "type": "Too many locals",
                "severity": Severity.MEDIUM,
                "detail": f"{local_count} local variables",
            })

        # =============================================
        # RETURNS
        # =============================================
        if return_count > 5:
            issues.append({
                "type": "Too many returns",
                "severity": Severity.LOW,
                "detail": f"{return_count} return statements",
            })

        # =============================================
        # DOCSTRING
        # =============================================
        if not metrics["has_docstring"]:
            issues.append({
                "type": "No docstring",
                "severity": Severity.LOW,
                "detail": "Function has no docstring",
            })

        return issues