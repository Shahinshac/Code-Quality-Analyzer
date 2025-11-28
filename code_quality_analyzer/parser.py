import ast
import astunparse
from typing import Dict, List


class ASTFeatureExtractor(ast.NodeVisitor):
    def __init__(self):
        self.features: Dict[str, int] = {
            "num_functions": 0,
            "avg_function_length": 0,
            "max_function_length": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_assignments": 0,
            "max_nesting": 0,
        }
        self._function_lengths: List[int] = []
        self._current_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.features["num_functions"] += 1
        start_lineno = node.lineno
        end_lineno = getattr(node, 'end_lineno', None)
        if end_lineno is None:
            # fallback: estimate from body nodes
            max_lineno = start_lineno
            for n in ast.walk(node):
                if hasattr(n, 'lineno'):
                    max_lineno = max(max_lineno, n.lineno)
            end_lineno = max_lineno
        length = end_lineno - start_lineno + 1
        self._function_lengths.append(length)
        self.features["max_function_length"] = max(self.features["max_function_length"], length)

        # measure nesting depth inside function
        prev_depth = self._current_depth
        self._current_depth = 0
        self.generic_visit(node)
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self._current_depth = prev_depth

    def visit_ClassDef(self, node: ast.ClassDef):
        self.features["num_classes"] += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.features["num_imports"] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.features["num_imports"] += 1
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        self.features["num_assignments"] += 1
        self.generic_visit(node)

    # Track nesting by counting compound statements
    def visit_If(self, node: ast.If):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_For(self, node: ast.For):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_While(self, node: ast.While):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_With(self, node: ast.With):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def extract_features(self, source: str) -> Dict[str, float]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            raise
        self.visit(tree)
        if self._function_lengths:
            self.features["avg_function_length"] = sum(self._function_lengths) / len(self._function_lengths)
        else:
            self.features["avg_function_length"] = 0
        return self.features


def extract_features_from_file(path: str) -> Dict[str, float]:
    with open(path, 'r', encoding='utf8') as fh:
        src = fh.read()
    ext = ASTFeatureExtractor()
    return ext.extract_features(src)


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    feat = extract_features_from_file(path)
    print(feat)
