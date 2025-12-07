"""
Universal Auto-Fixer for Multiple Languages
"""
import re
from typing import Tuple, List, Dict


class UniversalAutoFixer:
    def __init__(self, language='python'):
        self.language = language.lower()
        self.fixes_applied = []
    
    def fix_all(self, code):
        fixed = code
        self.fixes_applied = []
        
        # Apply language-specific fixes
        fixed = self._fix_whitespace(fixed)
        fixed = self._fix_long_lines(fixed)
        fixed = self._add_missing_semicolons(fixed)
        fixed = self._fix_indentation(fixed)
        
        return fixed, self.fixes_applied
    
    def _fix_whitespace(self, code):
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original = line
            # Remove trailing whitespace
            line = line.rstrip()
            
            if line != original:
                self.fixes_applied.append({
                    'type': 'whitespace',
                    'message': 'Removed trailing whitespace',
                    'line': i + 1
                })
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_long_lines(self, code):
        # Just log long lines, don't actually break them (complex logic)
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.fixes_applied.append({
                    'type': 'style',
                    'message': f'Line exceeds 120 characters ({len(line)} chars)',
                    'line': i
                })
        
        return code
    
    def _add_missing_semicolons(self, code):
        if self.language not in ['javascript', 'typescript', 'java', 'cpp', 'csharp', 'css']:
            return code
        
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Add semicolon if missing (simple heuristic)
            if self.language == 'css':
                # CSS property declarations need semicolons
                if stripped and ':' in stripped and not stripped.endswith((';', '{', '}')):
                    line = line.rstrip() + ';'
                    self.fixes_applied.append({
                        'type': 'syntax',
                        'message': 'Added missing semicolon in CSS',
                        'line': i + 1
                    })
            elif stripped and not stripped.endswith((';', '{', '}', ':', ',')) and not stripped.startswith(('if', 'for', 'while', 'function', 'class')):
                if re.match(r'^\s*(const|let|var|return)\s+', line):
                    line = line.rstrip() + ';'
                    self.fixes_applied.append({
                        'type': 'syntax',
                        'message': 'Added missing semicolon',
                        'line': i + 1
                    })
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_indentation(self, code):
        lines = code.split('\n')
        indent_size = self._detect_indent_size(lines)
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                fixed_lines.append('')
                continue
            
            # Normalize indentation to detected size
            current_indent = len(line) - len(line.lstrip())
            if current_indent % indent_size != 0:
                normalized_indent = (current_indent // indent_size) * indent_size
                fixed = ' ' * normalized_indent + line.lstrip()
                fixed_lines.append(fixed)
                
                if fixed != line:
                    self.fixes_applied.append({
                        'type': 'indentation',
                        'message': f'Normalized indentation to {indent_size} spaces',
                        'line': i + 1
                    })
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _detect_indent_size(self, lines):
        indents = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)
        
        if not indents:
            return 4
        
        # Find most common indent
        from collections import Counter
        common = Counter(indents).most_common(1)
        return common[0][0] if common else 4
