import ast

class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 0

    def analyze(self, node):
        self.complexity = 1  # start from 1
        self.visit(node)
        return self.complexity

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)