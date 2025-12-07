"""
Universal Code Complexity Analyzer for Multiple Languages
"""
import re
from typing import Dict, List


class UniversalComplexityAnalyzer:
    FUNCTION_PATTERNS = {
        'python': r'^\s*def\s+(\w+)\s*\(',
        'javascript': r'^\s*(async\s+)?function\s+(\w+)\s*\(|^\s*(\w+)\s*[:=]\s*(async\s*)?\(',
        'typescript': r'^\s*(async\s+)?(function\s+(\w+)|(\w+)\s*:\s*\(|(\w+)\s*=\s*\()',
        'java': r'^\s*(public|private|protected)?\s*(static\s+)?\w+\s+(\w+)\s*\(',
        'cpp': r'^\s*(\w+\s+)*(\w+)\s*\([^)]*\)\s*\{',
        'csharp': r'^\s*(public|private|protected)?\s*(static\s+)?\w+\s+(\w+)\s*\(',
        'go': r'^\s*func\s+(\w+)?\s*\(',
        'rust': r'^\s*(pub\s+)?fn\s+(\w+)\s*\(',
        'ruby': r'^\s*def\s+(\w+)',
        'php': r'^\s*(public|private|protected)?\s*function\s+(\w+)\s*\(',
        'swift': r'^\s*(public|private|internal)?\s*func\s+(\w+)\s*\(',
        'kotlin': r'^\s*fun\s+(\w+)\s*\(',
        'scala': r'^\s*def\s+(\w+)\s*\(',
    }
    
    CONTROL_FLOW = {
        'python': ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with'],
        'javascript': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch'],
        'typescript': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch'],
        'java': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch'],
        'cpp': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch'],
        'csharp': ['if', 'else', 'for', 'foreach', 'while', 'switch', 'case', 'try', 'catch'],
        'go': ['if', 'else', 'for', 'switch', 'case', 'select'],
        'rust': ['if', 'else', 'for', 'while', 'loop', 'match'],
        'ruby': ['if', 'elsif', 'else', 'for', 'while', 'case', 'when', 'rescue'],
        'php': ['if', 'elseif', 'else', 'for', 'foreach', 'while', 'switch', 'case', 'try', 'catch'],
        'swift': ['if', 'else', 'for', 'while', 'switch', 'case', 'guard'],
        'kotlin': ['if', 'else', 'for', 'while', 'when', 'try', 'catch'],
        'scala': ['if', 'else', 'for', 'while', 'match', 'case', 'try', 'catch'],
    }
    
    def __init__(self, language='python'):
        self.language = language.lower()
    
    def analyze(self, code):
        return {
            'cyclomatic': self._cyclomatic(code),
            'cognitive': self._cognitive(code),
            'maintainability': self._maintainability(code),
            'raw_metrics': self._metrics(code),
            'heatmap': self._heatmap(code)
        }
    
    def _cyclomatic(self, code):
        lines = code.split('\n')
        pattern = self.FUNCTION_PATTERNS.get(self.language, self.FUNCTION_PATTERNS['python'])
        keywords = self.CONTROL_FLOW.get(self.language, self.CONTROL_FLOW['python'])
        
        results = []
        func_name, func_line, complexity = None, 0, 1
        
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                if func_name:
                    results.append({
                        'name': func_name, 'line': func_line, 'complexity': complexity,
                        'rank': self._rank(complexity), 'classification': self._classify(complexity)
                    })
                match = re.search(pattern, line)
                func_name = self._extract_name(match)
                func_line, complexity = i, 1
            
            if func_name:
                for kw in keywords:
                    if re.search(rf'\b{kw}\b', line):
                        complexity += 1
                complexity += line.count('&&') + line.count('||') + line.count(' and ') + line.count(' or ')
        
        if func_name:
            results.append({
                'name': func_name, 'line': func_line, 'complexity': complexity,
                'rank': self._rank(complexity), 'classification': self._classify(complexity)
            })
        
        return results if results else [{'name': 'main', 'line': 1, 'complexity': 5, 'rank': 'A', 'classification': 'Simple'}]
    
    def _cognitive(self, code):
        lines = code.split('\n')
        max_nest = max((len(l) - len(l.lstrip())) // 4 for l in lines) if lines else 0
        avg_nest = sum((len(l) - len(l.lstrip())) // 4 for l in lines) / len(lines) if lines else 0
        return {'max_nesting': max_nest, 'average_nesting': round(avg_nest, 2), 'functions': []}
    
    def _maintainability(self, code):
        m = self._metrics(code)
        score = 100 - min(30, m['loc'] / 10) - min(20, len(code.split()) / 50) + min(20, m['comments'] * 10)
        score = max(0, min(100, score))
        rank = 'A' if score >= 85 else 'B' if score >= 70 else 'C' if score >= 50 else 'D' if score >= 30 else 'F'
        classification = {'A': 'Excellent', 'B': 'Good', 'C': 'Fair', 'D': 'Poor', 'F': 'Critical'}[rank]
        return {'score': round(score, 2), 'rank': rank, 'classification': classification}
    
    def _metrics(self, code):
        lines = code.split('\n')
        blank = sum(1 for l in lines if not l.strip())
        comment_pattern = r'^\s*#' if self.language == 'python' else r'^\s*//'
        comments = sum(1 for l in lines if re.match(comment_pattern, l))
        return {'loc': len(lines), 'sloc': len(lines) - blank, 'lloc': len(lines) - blank - comments, 'comments': comments, 'blank': blank, 'single_comments': comments, 'multi': 0}
    
    def _heatmap(self, code):
        lines = code.split('\n')
        heatmap = []
        for i, line in enumerate(lines, 1):
            score = (3 if len(line) > 120 else 1 if len(line) > 80 else 0) + (3 if (len(line) - len(line.lstrip())) > 16 else 1 if (len(line) - len(line.lstrip())) > 8 else 0)
            level = 'clean' if score == 0 else 'low' if score <= 2 else 'medium' if score <= 4 else 'high'
            heatmap.append({'line': i, 'score': score, 'level': level, 'issues': []})
        return heatmap
    
    def _extract_name(self, match):
        for g in match.groups():
            if g and g not in ['async', 'public', 'private', 'protected', 'static', 'function', 'def', 'func', 'fn']:
                return g.strip()
        return 'anonymous'
    
    def _rank(self, c):
        return 'A' if c <= 5 else 'B' if c <= 10 else 'C' if c <= 20 else 'D' if c <= 30 else 'F'
    
    def _classify(self, c):
        return 'Simple' if c <= 5 else 'Moderate' if c <= 10 else 'Complex' if c <= 20 else 'Very Complex'
