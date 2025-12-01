import ast
import re
import os
from typing import List, Dict, Optional
from .parser import PythonFeatureExtractor, detect_language
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
        extractor = PythonFeatureExtractor()
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

    def detect_javascript_issues(self, source: str) -> List[CodeSmell]:
        """Detect JavaScript/TypeScript issues using ESLint if available"""
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.js', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            # Try ESLint
            cmd = ['eslint', tmp_fn, '--format', 'json', '--no-eslintrc']
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode in [0, 1]:  # ESLint returns 1 if issues found
                import json
                results = json.loads(proc.stdout)
                for file_result in results:
                    for msg in file_result.get('messages', []):
                        smells.append(CodeSmell(
                            'eslint',
                            f"[{msg.get('ruleId', 'unknown')}] {msg.get('message', '')}",
                            msg.get('line')
                        ))
        except FileNotFoundError:
            # ESLint not installed, skip
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_java_issues(self, source: str) -> List[CodeSmell]:
        """Detect Java issues using Checkstyle or PMD if available"""
        smells = []
        
        # Try Checkstyle
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.java', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            # Try checkstyle command
            cmd = ['checkstyle', '-f', 'xml', tmp_fn]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0 and '<error' in proc.stdout:
                # Parse XML output for errors
                import xml.etree.ElementTree as ET
                root = ET.fromstring(proc.stdout)
                for error in root.findall('.//error'):
                    smells.append(CodeSmell(
                        'checkstyle',
                        f"[{error.get('source', 'unknown')}] {error.get('message', '')}",
                        int(error.get('line', 0))
                    ))
        except FileNotFoundError:
            # Checkstyle not installed, fallback to basic heuristics
            smells.extend(self._java_basic_heuristics(source))
        except Exception:
            smells.extend(self._java_basic_heuristics(source))
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        
        return smells

    def _java_basic_heuristics(self, source: str, max_method_length: int = 80, max_nesting: int = 4) -> List[CodeSmell]:
        """Basic Java heuristics when linters not available"""
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

    def detect_cpp_issues(self, source: str) -> List[CodeSmell]:
        """Detect C++ issues using cppcheck if available"""
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cpp', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            cmd = ['cppcheck', '--enable=all', '--template={line}:{severity}:{message}', tmp_fn]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            output = proc.stderr  # cppcheck outputs to stderr
            
            for line in output.splitlines():
                if ':' in line:
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        try:
                            lineno = int(parts[0])
                            severity = parts[1]
                            message = parts[2]
                            smells.append(CodeSmell(f'cppcheck_{severity}', message.strip(), lineno))
                        except ValueError:
                            continue
        except FileNotFoundError:
            # cppcheck not installed
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_go_issues(self, source: str) -> List[CodeSmell]:
        """Detect Go issues using golangci-lint if available"""
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.go', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            cmd = ['golangci-lint', 'run', '--out-format', 'json', tmp_fn]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            
            if proc.stdout:
                import json
                results = json.loads(proc.stdout)
                for issue in results.get('Issues', []):
                    smells.append(CodeSmell(
                        f"golangci_{issue.get('FromLinter', 'unknown')}",
                        issue.get('Text', ''),
                        issue.get('Pos', {}).get('Line')
                    ))
        except FileNotFoundError:
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_rust_issues(self, source: str) -> List[CodeSmell]:
        """Detect Rust issues using clippy if available"""
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.rs', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            cmd = ['cargo', 'clippy', '--', '-W', 'clippy::all', '--message-format', 'json']
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(tmp_fn))
            
            for line in proc.stdout.splitlines():
                if line.strip():
                    try:
                        import json
                        msg = json.loads(line)
                        if msg.get('reason') == 'compiler-message':
                            message = msg.get('message', {})
                            smells.append(CodeSmell(
                                'clippy',
                                message.get('message', ''),
                                message.get('spans', [{}])[0].get('line_start')
                            ))
                    except Exception:
                        continue
        except FileNotFoundError:
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_ruby_issues(self, source: str) -> List[CodeSmell]:
        """Detect Ruby issues using RuboCop if available"""
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.rb', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            cmd = ['rubocop', '--format', 'json', tmp_fn]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            
            if proc.stdout:
                import json
                results = json.loads(proc.stdout)
                for file_result in results.get('files', []):
                    for offense in file_result.get('offenses', []):
                        smells.append(CodeSmell(
                            f"rubocop_{offense.get('cop_name', 'unknown')}",
                            offense.get('message', ''),
                            offense.get('location', {}).get('line')
                        ))
        except FileNotFoundError:
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_php_issues(self, source: str) -> List[CodeSmell]:
        """Detect PHP issues using PHP_CodeSniffer if available"""
        smells = []
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.php', encoding='utf8') as tmp:
                tmp.write(source)
                tmp.flush()
                tmp_fn = tmp.name
            
            cmd = ['phpcs', '--report=json', tmp_fn]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            
            if proc.stdout:
                import json
                results = json.loads(proc.stdout)
                for file_path, file_data in results.get('files', {}).items():
                    for message in file_data.get('messages', []):
                        smells.append(CodeSmell(
                            f"phpcs_{message.get('source', 'unknown')}",
                            message.get('message', ''),
                            message.get('line')
                        ))
        except FileNotFoundError:
            pass
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_fn)
            except Exception:
                pass
        return smells

    def detect_all_languages(self, source: str, language: str) -> List[CodeSmell]:
        """Detect issues for any supported language"""
        smells = []
        
        if language == 'python':
            smells.extend(self.detect_all(source))
        elif language in ['javascript', 'typescript']:
            smells.extend(self.detect_javascript_issues(source))
        elif language == 'java':
            smells.extend(self.detect_java_issues(source))
        elif language == 'cpp':
            smells.extend(self.detect_cpp_issues(source))
        elif language == 'go':
            smells.extend(self.detect_go_issues(source))
        elif language == 'rust':
            smells.extend(self.detect_rust_issues(source))
        elif language == 'ruby':
            smells.extend(self.detect_ruby_issues(source))
        elif language == 'php':
            smells.extend(self.detect_php_issues(source))
        
        return smells


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python detectors.py <file_path>")
        sys.exit(1)
    
    path = sys.argv[1]
    with open(path, 'r', encoding='utf8') as fh:
        src = fh.read()
    
    language = detect_language(path, src)
    print(f"Detected language: {language}")
    
    det = RuleBasedDetector()
    smells = det.detect_all_languages(src, language)
    print(f"Found {len(smells)} code smells:")
    for smell in smells:
        print(f"  {smell.to_dict()}")
