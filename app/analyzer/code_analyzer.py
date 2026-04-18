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

    def find_long_functions(self, max_lines=10):
        long_functions = []

        for func in self.get_functions():
            start = func.lineno
            end = getattr(func, "end_lineno", start)
            length = end - start + 1

            if length > max_lines:
                long_functions.append({
                    "name": func.name,
                    "length": length
                })

        return long_functions

    def find_functions_with_many_args(self, max_args=4):
        flagged = []

        for func in self.get_functions():
            num_args = len(func.args.args)

            if num_args > max_args:
                flagged.append({
                    "name": func.name,
                    "args": num_args
                })

        return flagged