import ast
from typing import List, Dict
from .parser import ASTFeatureExtractor
import subprocess
import tempfile


class CodeSmell:
    def __init__(self, kind: str, message: str, lineno: int = None):
        self.kind = kind
        self.message = message
        self.lineno = lineno

    def to_dict(self):
        return {
            "kind": self.kind,
            "message": self.message,
            "lineno": self.lineno,
        }


class RuleBasedDetector:
    def __init__(self, max_function_length=40, max_nesting=4):
        self.max_function_length = max_function_length
        self.max_nesting = max_nesting

    def detect_long_functions(self, source: str) -> List[CodeSmell]:
        smells = []
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno
                end = getattr(node, 'end_lineno', None)
                if end is None:
                    maxl = start
                    for n in ast.walk(node):
                        if hasattr(n, 'lineno'):
                            maxl = max(maxl, n.lineno)
                    end = maxl
                length = end - start + 1
                if length > self.max_function_length:
                    smells.append(CodeSmell('long_function', f'Function {node.name} is too long ({length} lines)', start))
        return smells

    def detect_deep_nesting(self, source: str) -> List[CodeSmell]:
        extractor = ASTFeatureExtractor()
        features = extractor.extract_features(source)
        smells = []
        if features.get('max_nesting', 0) > self.max_nesting:
            smells.append(CodeSmell('deep_nesting', f'Max nesting depth is {features.get("max_nesting")}', None))
        return smells

    def detect_unused_imports(self, source: str) -> List[CodeSmell]:
        tree = ast.parse(source)
        imports = {}
        usages = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name.split('.')[0]] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.lineno
            elif isinstance(node, ast.Name):
                usages.add(node.id)
        smells = []
        for name, lineno in imports.items():
            if name not in usages:
                smells.append(CodeSmell('unused_import', f'Import {name} is unused', lineno))
        return smells

    def detect_unused_variables(self, source: str) -> List[CodeSmell]:
        # Basic heuristic: variable assigned but not used (in same file)
        tree = ast.parse(source)
        assigned = set()
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        assigned.add(t.id)
            elif isinstance(node, ast.AugAssign):
                t = node.target
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
            elif isinstance(node, ast.Name):
                used.add(node.id)
        smells = []
        for var in assigned:
            if var not in used:
                smells.append(CodeSmell('unused_variable', f'Variable {var} is assigned but never used'))
        return smells

    def detect_all(self, source: str) -> List[CodeSmell]:
        smells = []
        smells.extend(self.detect_long_functions(source))
        smells.extend(self.detect_deep_nesting(source))
        smells.extend(self.detect_unused_imports(source))
        smells.extend(self.detect_unused_variables(source))
        # flake8 rule-based lints
        try:
            smells.extend(self.detect_with_flake8(source))
        except Exception:
            pass
        try:
            smells.extend(self.detect_with_pylint(source))
        except Exception:
            pass
        return smells

    def detect_with_flake8(self, source: str) -> List[CodeSmell]:
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            import sys
            cmd = [sys.executable, '-m', 'flake8', tmp_fn, '--format=%(row)d:%(col)d:%(code)s:%(text)s']
            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = proc.stdout.strip()
            for line in out.splitlines():
                if not line:
                    continue
                parts = line.split(':', 3)
                if len(parts) == 4:
                    row, col, code, text = parts
                    msg = f'[{code}] {text.strip()}'
                    smells.append(CodeSmell('flake8', msg, int(row)))
        finally:
            try:
                import os
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_with_pylint(self, source: str) -> List[CodeSmell]:
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            import sys
            cmd = [sys.executable, '-m', 'pylint', '--output-format', 'text', tmp_fn]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            out = proc.stdout.strip()
            for line in out.splitlines():
                if ':' in line:
                    parts = line.split(':', 3)
                    if len(parts) >= 3:
                        try:
                            row = int(parts[1])
                        except Exception:
                            row = None
                        msg = parts[-1].strip()
                        smells.append(CodeSmell('pylint', msg, row))
        finally:
            try:
                import os
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_java_issues(self, source: str, max_method_length: int = 80, max_nesting: int = 4) -> List[CodeSmell]:
        # Basic Java heuristics: find method signatures and count lines until closing brace
        import re
        smells = []
        lines = source.splitlines()
        pattern = re.compile(r"\b(public|private|protected|static)\b.*\(.*\)\s*\{")
        i = 0
        while i < len(lines):
            line = lines[i]
            if pattern.search(line):
                start = i
                depth = 0
                end = start
                for j in range(i, len(lines)):
                    l = lines[j]
                    depth += l.count('{') - l.count('}')
                    if depth <= 0:
                        end = j
                        break
                length = end - start + 1
                if length > max_method_length:
                    smells.append(CodeSmell('java_long_method', f'Java method too long ({length} lines)', start+1))
                # A simple nesting detection inside the method
                nesting = 0
                max_n = 0
                for k in range(start, end+1):
                    nesting += lines[k].count('{') - lines[k].count('}')
                    max_n = max(max_n, nesting)
                if max_n > max_nesting:
                    smells.append(CodeSmell('java_deep_nesting', f'Max nesting inside Java method is {max_n}', start+1))
                i = end + 1
            else:
                i += 1
        return smells


if __name__ == '__main__':
    import sys
    path = sys.argv[1]
    with open(path, 'r', encoding='utf8') as fh:
        src = fh.read()
    det = RuleBasedDetector()
    smells = det.detect_all(src)
    print([s.to_dict() for s in smells])
