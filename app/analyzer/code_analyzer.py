from app.analyzer.complexity_analyzer import ComplexityAnalyzer
import ast


class CodeAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tree = None

    def load_file(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.tree = ast.parse(code)

    def get_functions(self):
        functions = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node)

        return functions

    # 🔥 NEW: suggestion system
    def get_suggestion(self, issue_type):
        suggestions = {
            "Too long": "Break this function into smaller functions.",
            "Too many arguments": "Consider grouping parameters into a class or dictionary.",
            "Too complex": "Reduce nested logic or split into smaller functions."
        }
        return suggestions.get(issue_type, "No suggestion available.")

    def full_analysis(self):
        results = []

        for func in self.get_functions():
            analyzer = ComplexityAnalyzer()
            complexity = analyzer.analyze(func)

            start = func.lineno
            end = getattr(func, "end_lineno", start)
            length = end - start + 1

            num_args = len(func.args.args)

            issues = []

            # ✅ FIXED: conditions restored
            if length > 10:
                issues.append({
                    "type": "Too long",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Too long")
                })

            if num_args > 4:
                issues.append({
                    "type": "Too many arguments",
                    "severity": "Medium",
                    "suggestion": self.get_suggestion("Too many arguments")
                })

            if complexity > 10:
                issues.append({
                    "type": "Too complex",
                    "severity": "High",
                    "suggestion": self.get_suggestion("Too complex")
                })

            # scoring system
            score = 10

            for issue in issues:
                if issue["severity"] == "High":
                    score -= 3
                elif issue["severity"] == "Medium":
                    score -= 2

            score = max(score, 0)

            results.append({
                "name": func.name,
                "length": length,
                "args": num_args,
                "complexity": complexity,
                "issues": issues,
                "score": score
            })

        return results

    def get_worst_functions(self):
        results = self.full_analysis()
        return sorted(results, key=lambda x: x["score"])

    def get_problematic_functions(self):
        results = self.full_analysis()
        return [r for r in results if r["issues"]]

    def get_critical_functions(self):
        results = self.full_analysis()
        critical = []

        for r in results:
            high_issues = [i for i in r["issues"] if i["severity"] == "High"]

            if high_issues:
                critical.append({
                    "name": r["name"],
                    "score": r["score"],
                    "issues": high_issues
                })

        return critical