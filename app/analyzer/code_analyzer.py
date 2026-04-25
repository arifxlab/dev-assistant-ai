from app.analyzer.complexity_analyzer import ComplexityAnalyzer
import ast


class CodeAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None

    # ---------------------------
    # LOAD CODE
    # ---------------------------
    def load_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.tree = ast.parse(code)

    # ---------------------------
    # GET FUNCTIONS
    # ---------------------------
    def get_functions(self):
        return [
            node for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef)
        ]

    # ---------------------------
    # NESTING DETECTOR (FIXED)
    # ---------------------------
    def get_max_nesting(self, node, depth=0):
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                max_depth = max(max_depth, self.get_max_nesting(child, depth + 1))
            else:
                max_depth = max(max_depth, self.get_max_nesting(child, depth))

        return max_depth

    # ---------------------------
    # SMART AI SUGGESTIONS
    # ---------------------------
    def get_suggestion(self, issue_type, func_name=None, value=None):
        if issue_type == "Too long":
            return f"Function '{func_name}' is too long. Break it into smaller helper functions."

        if issue_type == "Too many arguments":
            return (
                f"Function '{func_name}' has {value} parameters. "
                "Group related parameters into a class or dictionary."
            )

        if issue_type == "Too complex":
            return (
                f"Function '{func_name}' has high complexity. "
                "Reduce nested conditions or split logic into smaller functions."
            )

        if issue_type == "Deep nesting":
            return (
                f"Function '{func_name}' has deep nesting. "
                "Use early returns or split logic into helper functions."
            )

        if issue_type == "God Function":
            return (
                f"Function '{func_name}' is doing too much. "
                "Split it into smaller functions with single responsibility."
            )

        return "No suggestion available."

    # ---------------------------
    # CORE ANALYSIS ENGINE
    # ---------------------------
    def full_analysis(self):
        results = []

        for func in self.get_functions():
            analyzer = ComplexityAnalyzer()
            complexity = analyzer.analyze(func)

            length = getattr(func, "end_lineno", func.lineno) - func.lineno + 1
            num_args = len(func.args.args)
            nesting = self.get_max_nesting(func)

            issues = []

            # BASIC RULES
            if length > 10:
                issues.append({
                    "type": "Too long",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Too long", func.name)
                })

            if num_args > 4:
                issues.append({
                    "type": "Too many arguments",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Too many arguments", func.name, num_args)
                })

            if complexity > 10:
                issues.append({
                    "type": "Too complex",
                    "severity": "High",
                    "suggestion": self.get_suggestion("Too complex", func.name)
                })

            # 🔥 DEEP NESTING
            if nesting >= 3:
                issues.append({
                    "type": "Deep nesting",
                    "severity": "High",
                    "suggestion": self.get_suggestion("Deep nesting", func.name)
                })

            # 🔥 GOD FUNCTION
            if length > 30 or complexity > 15:
                issues.append({
                    "type": "God Function",
                    "severity": "High",
                    "suggestion": self.get_suggestion("God Function", func.name)
                })

            # ---------------------------
            # SCORING SYSTEM
            # ---------------------------
            score = 10

            for issue in issues:
                if issue["severity"] == "High":
                    score -= 3
                elif issue["severity"] == "Medium":
                    score -= 2

            # extra penalty for deep nesting
            if nesting >= 3:
                score -= 2

            score = max(score, 0)

            results.append({
                "name": func.name,
                "length": length,
                "args": num_args,
                "complexity": complexity,
                "nesting": nesting,
                "issues": issues,
                "score": score
            })

        return results

    # ---------------------------
    # WORST FUNCTIONS
    # ---------------------------
    def get_worst_functions(self):
        return sorted(self.full_analysis(), key=lambda x: x["score"])

    # ---------------------------
    # PROBLEMATIC FUNCTIONS
    # ---------------------------
    def get_problematic_functions(self):
        return [r for r in self.full_analysis() if r["issues"]]

    # ---------------------------
    # CRITICAL FUNCTIONS
    # ---------------------------
    def get_critical_functions(self):
        results = self.full_analysis()

        return [
            {
                "name": r["name"],
                "score": r["score"],
                "issues": [i for i in r["issues"] if i["severity"] == "High"]
            }
            for r in results
            if any(i["severity"] == "High" for i in r["issues"])
        ]