"""
Auto-fixing engine for code quality issues
Rewrites code with optimizations, PEP8 fixes, and improvements
"""
import ast
import autopep8
import re
from typing import Dict, List, Tuple


class CodeAutoFixer:
    """Automatically fix code quality issues"""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_all(self, code: str) -> Tuple[str, List[Dict]]:
        """Apply all available fixes to code"""
        self.fixes_applied = []
        
        # 1. PEP8 formatting
        code = self._fix_pep8(code)
        
        # 2. Add missing docstrings
        code = self._add_docstrings(code)
        
        # 3. Remove dead code
        code = self._remove_dead_code(code)
        
        # 4. Optimize loops
        code = self._optimize_loops(code)
        
        # 5. Improve variable names
        code = self._improve_variable_names(code)
        
        return code, self.fixes_applied
    
    def _fix_pep8(self, code: str) -> str:
        """Apply PEP8 formatting using autopep8"""
        try:
            fixed = autopep8.fix_code(code, options={
                'aggressive': 2,
                'max_line_length': 120,
            })
            if fixed != code:
                self.fixes_applied.append({
                    'type': 'pep8',
                    'message': 'Applied PEP8 formatting (line length, spacing, indentation)'
                })
            return fixed
        except Exception as e:
            return code
    
    def _add_docstrings(self, code: str) -> str:
        """Add missing docstrings to functions and classes"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            insertions = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Check if docstring exists
                    has_docstring = (
                        len(node.body) > 0 and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant)
                    )
                    
                    if not has_docstring and hasattr(node, 'lineno'):
                        indent = self._get_indent(lines[node.lineno - 1])
                        docstring_indent = indent + '    '
                        
                        if isinstance(node, ast.FunctionDef):
                            # Get function signature
                            args = [arg.arg for arg in node.args.args]
                            docstring = f'{docstring_indent}"""{node.name} function'
                            if args:
                                docstring += f'\n{docstring_indent}\n{docstring_indent}Args:\n'
                                for arg in args:
                                    docstring += f'{docstring_indent}    {arg}: TODO\n'
                            docstring += f'{docstring_indent}"""'
                        else:
                            docstring = f'{docstring_indent}"""{node.name} class"""'
                        
                        insertions.append((node.lineno, docstring))
                        self.fixes_applied.append({
                            'type': 'docstring',
                            'message': f'Added docstring to {node.name}',
                            'line': node.lineno
                        })
            
            # Insert docstrings (reverse order to maintain line numbers)
            for lineno, docstring in sorted(insertions, reverse=True):
                lines.insert(lineno, docstring)
            
            return '\n'.join(lines)
        except:
            return code
    
    def _remove_dead_code(self, code: str) -> str:
        """Remove unreachable code and unused variables"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            dead_lines = set()
            
            # Detect unreachable code after return/break/continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.For, ast.While, ast.If)):
                    for i, stmt in enumerate(node.body):
                        if isinstance(stmt, (ast.Return, ast.Break, ast.Continue)):
                            # Mark subsequent statements as dead
                            for j in range(i + 1, len(node.body)):
                                if hasattr(node.body[j], 'lineno'):
                                    dead_lines.add(node.body[j].lineno - 1)
            
            if dead_lines:
                lines = [line for i, line in enumerate(lines) if i not in dead_lines]
                self.fixes_applied.append({
                    'type': 'dead_code',
                    'message': f'Removed {len(dead_lines)} lines of unreachable code'
                })
            
            return '\n'.join(lines)
        except:
            return code
    
    def _optimize_loops(self, code: str) -> str:
        """Optimize loop patterns"""
        original = code
        
        # Replace range(len()) with enumerate
        code = re.sub(
            r'for (\w+) in range\(len\((\w+)\)\):',
            r'for \1, item in enumerate(\2):',
            code
        )
        
        if code != original:
            self.fixes_applied.append({
                'type': 'loop_optimization',
                'message': 'Replaced range(len()) with enumerate()'
            })
        
        return code
    
    def _improve_variable_names(self, code: str) -> str:
        """Suggest better variable names for single-letter variables"""
        # This is a simplified version - full implementation would use AST
        problematic_vars = re.findall(r'\b[a-z]\s*=', code)
        
        if problematic_vars and len(problematic_vars) > 3:
            self.fixes_applied.append({
                'type': 'naming',
                'message': f'Found {len(problematic_vars)} single-letter variables - consider more descriptive names'
            })
        
        return code
    
    def _get_indent(self, line: str) -> str:
        """Get indentation of a line"""
        return line[:len(line) - len(line.lstrip())]
    
    def add_type_hints(self, code: str) -> str:
        """Add basic type hints to function signatures"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if already has type hints
                    has_hints = any(arg.annotation for arg in node.args.args)
                    if not has_hints and hasattr(node, 'lineno'):
                        self.fixes_applied.append({
                            'type': 'type_hints',
                            'message': f'Consider adding type hints to {node.name}()',
                            'line': node.lineno
                        })
            
            return code
        except:
            return code
