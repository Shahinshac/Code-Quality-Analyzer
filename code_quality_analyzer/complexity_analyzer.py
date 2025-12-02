"""
Code Complexity Analysis using Radon and custom metrics
Generates complexity heatmap data
"""
from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit, mi_rank
from radon.raw import analyze
import ast
from typing import Dict, List


class ComplexityAnalyzer:
    """Analyze code complexity and generate heatmap data"""
    
    def analyze(self, code: str) -> Dict:
        """Comprehensive complexity analysis"""
        results = {
            'cyclomatic': self._cyclomatic_complexity(code),
            'cognitive': self._cognitive_complexity(code),
            'maintainability': self._maintainability_index(code),
            'raw_metrics': self._raw_metrics(code),
            'heatmap': self._generate_heatmap(code)
        }
        return results
    
    def _cyclomatic_complexity(self, code: str) -> List[Dict]:
        """Calculate cyclomatic complexity for all functions"""
        try:
            complexity_data = cc_visit(code)
            results = []
            
            for item in complexity_data:
                results.append({
                    'name': item.name,
                    'line': item.lineno,
                    'complexity': item.complexity,
                    'rank': cc_rank(item.complexity),
                    'classification': self._classify_complexity(item.complexity)
                })
            
            return results
        except:
            return []
    
    def _cognitive_complexity(self, code: str) -> Dict:
        """Calculate cognitive complexity (custom metric)"""
        try:
            tree = ast.parse(code)
            total_nesting = 0
            max_nesting = 0
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    nesting = self._calculate_nesting_depth(node)
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'nesting_depth': nesting
                    })
                    max_nesting = max(max_nesting, nesting)
                    total_nesting += nesting
            
            return {
                'max_nesting': max_nesting,
                'average_nesting': total_nesting / len(functions) if functions else 0,
                'functions': functions
            }
        except:
            return {'max_nesting': 0, 'average_nesting': 0, 'functions': []}
    
    def _maintainability_index(self, code: str) -> Dict:
        """Calculate maintainability index"""
        try:
            mi_score = mi_visit(code, multi=True)
            rank = mi_rank(mi_score)
            
            return {
                'score': round(mi_score, 2),
                'rank': rank,
                'classification': self._classify_maintainability(rank)
            }
        except:
            return {'score': 0, 'rank': 'C', 'classification': 'Poor'}
    
    def _raw_metrics(self, code: str) -> Dict:
        """Get raw code metrics"""
        try:
            metrics = analyze(code)
            return {
                'loc': metrics.loc,  # Lines of code
                'lloc': metrics.lloc,  # Logical lines of code
                'sloc': metrics.sloc,  # Source lines of code
                'comments': metrics.comments,
                'multi': metrics.multi,  # Multi-line strings
                'blank': metrics.blank,
                'single_comments': metrics.single_comments
            }
        except:
            return {}
    
    def _generate_heatmap(self, code: str) -> List[Dict]:
        """Generate complexity heatmap data for visualization"""
        heatmap = []
        
        try:
            lines = code.split('\n')
            complexity_items = cc_visit(code)
            
            # Create line-by-line complexity map
            complexity_map = {}
            for item in complexity_items:
                complexity_map[item.lineno] = item.complexity
            
            tree = ast.parse(code)
            
            for i, line in enumerate(lines, 1):
                # Calculate line score based on multiple factors
                score = 0
                issues = []
                
                # Length penalty
                if len(line) > 120:
                    score += 3
                    issues.append('long_line')
                elif len(line) > 80:
                    score += 1
                
                # Complexity penalty
                if i in complexity_map:
                    complexity = complexity_map[i]
                    if complexity > 10:
                        score += 5
                        issues.append('high_complexity')
                    elif complexity > 5:
                        score += 2
                        issues.append('moderate_complexity')
                
                # Nesting penalty
                indent = len(line) - len(line.lstrip())
                if indent > 16:
                    score += 3
                    issues.append('deep_nesting')
                elif indent > 8:
                    score += 1
                
                heatmap.append({
                    'line': i,
                    'score': score,
                    'level': self._score_to_level(score),
                    'issues': issues
                })
            
            return heatmap
        except:
            return []
    
    def _calculate_nesting_depth(self, node, depth=0) -> int:
        """Calculate maximum nesting depth in a function"""
        max_depth = depth
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _classify_complexity(self, score: int) -> str:
        """Classify cyclomatic complexity score"""
        if score <= 5:
            return 'Simple'
        elif score <= 10:
            return 'Moderate'
        elif score <= 20:
            return 'Complex'
        else:
            return 'Very Complex'
    
    def _classify_maintainability(self, rank: str) -> str:
        """Classify maintainability rank"""
        classifications = {
            'A': 'Excellent',
            'B': 'Good',
            'C': 'Fair',
            'D': 'Poor',
            'F': 'Critical'
        }
        return classifications.get(rank, 'Unknown')
    
    def _score_to_level(self, score: int) -> str:
        """Convert numerical score to severity level"""
        if score == 0:
            return 'clean'
        elif score <= 2:
            return 'low'
        elif score <= 4:
            return 'medium'
        else:
            return 'high'
    
    def get_quality_score(self, analysis: Dict) -> float:
        """Calculate overall quality score (0-100) based on complexity metrics"""
        try:
            # Maintainability contributes 40%
            mi_score = analysis['maintainability'].get('score', 0)
            mi_contribution = (mi_score / 100) * 40
            
            # Cyclomatic complexity contributes 30%
            avg_complexity = sum(item['complexity'] for item in analysis['cyclomatic']) / len(analysis['cyclomatic']) if analysis['cyclomatic'] else 0
            complexity_contribution = max(0, 30 - (avg_complexity * 2))
            
            # Cognitive complexity contributes 30%
            avg_nesting = analysis['cognitive'].get('average_nesting', 0)
            cognitive_contribution = max(0, 30 - (avg_nesting * 5))
            
            total = mi_contribution + complexity_contribution + cognitive_contribution
            return round(min(100, max(0, total)), 2)
        except:
            return 50.0
