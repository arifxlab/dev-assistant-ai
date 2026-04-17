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