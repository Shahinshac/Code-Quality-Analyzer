"""
Enhanced Quality Scoring System
Combines multiple metrics into comprehensive 0-100 score
"""
from typing import Dict, List


class QualityScorer:
    """Calculate comprehensive quality score with weighted components"""
    
    def __init__(self):
        # Weight distribution (must sum to 100)
        self.weights = {
            'style': 18,           # PEP8 compliance
            'maintainability': 18,  # Maintainability index  
            'complexity': 26,       # Cyclomatic/cognitive complexity
            'security': 35,         # Security vulnerabilities (increased from 30)
            'documentation': 3      # Docstrings and comments
        }
    
    def calculate_score(
        self,
        smells: List,
        complexity_analysis: Dict = None,
        security_analysis: Dict = None,
        auto_fix_report: Dict = None
    ) -> Dict:
        """Calculate comprehensive quality score"""
        
        # Component scores
        style_score = self._calculate_style_score(smells, auto_fix_report)
        maintainability_score = self._calculate_maintainability_score(complexity_analysis)
        complexity_score = self._calculate_complexity_score(complexity_analysis)
        security_score = self._calculate_security_score(security_analysis)
        documentation_score = self._calculate_documentation_score(smells, auto_fix_report)
        
        # Weighted total
        total_score = (
            style_score * self.weights['style'] / 100 +
            maintainability_score * self.weights['maintainability'] / 100 +
            complexity_score * self.weights['complexity'] / 100 +
            security_score * self.weights['security'] / 100 +
            documentation_score * self.weights['documentation'] / 100
        )
        
        return {
            'total_score': round(total_score, 2),
            'grade': self._score_to_grade(total_score),
            'components': {
                'style': {
                    'score': round(style_score, 2),
                    'weight': self.weights['style'],
                    'contribution': round(style_score * self.weights['style'] / 100, 2)
                },
                'maintainability': {
                    'score': round(maintainability_score, 2),
                    'weight': self.weights['maintainability'],
                    'contribution': round(maintainability_score * self.weights['maintainability'] / 100, 2)
                },
                'complexity': {
                    'score': round(complexity_score, 2),
                    'weight': self.weights['complexity'],
                    'contribution': round(complexity_score * self.weights['complexity'] / 100, 2)
                },
                'security': {
                    'score': round(security_score, 2),
                    'weight': self.weights['security'],
                    'contribution': round(security_score * self.weights['security'] / 100, 2)
                },
                'documentation': {
                    'score': round(documentation_score, 2),
                    'weight': self.weights['documentation'],
                    'contribution': round(documentation_score * self.weights['documentation'] / 100, 2)
                }
            },
            'recommendations': self._generate_recommendations(
                style_score, maintainability_score, complexity_score,
                security_score, documentation_score
            )
        }
    
    def _calculate_style_score(self, smells: List, auto_fix_report: Dict) -> float:
        """Calculate PEP8 compliance score"""
        if not smells:
            return 100.0
        
        style_issues = [s for s in smells if hasattr(s, 'kind') and 
                       s.kind in ['long_line', 'trailing_whitespace', 'naming', 'poor_naming']]
        
        # Extremely aggressive penalties
        penalty = len(style_issues) * 12  # Increased from 8
        
        # Extra penalty for poor naming (very important)
        poor_naming = [s for s in style_issues if s.kind == 'poor_naming']
        penalty += len(poor_naming) * 20  # Increased from 15
        
        if auto_fix_report:
            pep8_fixes = len([f for f in auto_fix_report.get('fixes', []) 
                            if f.get('type') == 'pep8'])
            penalty += pep8_fixes * 3
            
            # Heavy penalty for naming issues (single-letter variables)
            naming_fixes = [f for f in auto_fix_report.get('fixes', []) 
                           if f.get('type') == 'naming']
            penalty += len(naming_fixes) * 20  # Increased from 15
        
        # Penalize missing docstrings
        docstring_issues = [f for f in auto_fix_report.get('fixes', []) 
                           if f.get('type') == 'docstring'] if auto_fix_report else []
        penalty += len(docstring_issues) * 12  # Increased from 8
        
        return max(0, 100 - penalty)
    
    def _calculate_maintainability_score(self, complexity_analysis: Dict) -> float:
        """Calculate maintainability score"""
        if not complexity_analysis:
            return 75.0  # Default score
        
        mi_data = complexity_analysis.get('maintainability', {})
        mi_score = mi_data.get('score', 75.0)
        
        # Apply penalty based on ranking
        rank = mi_data.get('rank', 'B')
        if rank == 'F':
            return max(0, mi_score - 30)
        elif rank == 'D':
            return max(0, mi_score - 20)
        elif rank == 'C':
            return max(0, mi_score - 10)
        
        return mi_score
    
    def _calculate_complexity_score(self, complexity_analysis: Dict) -> float:
        """Calculate complexity score"""
        if not complexity_analysis:
            return 75.0
        
        score = 100.0
        
        # Extremely aggressive cyclomatic complexity penalties
        cyclomatic = complexity_analysis.get('cyclomatic', [])
        for item in cyclomatic:
            complexity = item['complexity']
            if complexity > 20:
                score -= 40  # Very complex (increased from 30)
            elif complexity > 10:
                score -= 30  # Increased from 20
            elif complexity > 5:
                score -= 15  # Increased from 10
            elif complexity > 3:
                score -= 8   # Increased from 5
            elif complexity > 2:
                score -= 5   # Increased from 3
            elif complexity > 1:
                score -= 2   # Even complexity of 2 gets penalized
        
        # Extremely aggressive cognitive complexity penalty
        cognitive = complexity_analysis.get('cognitive', {})
        max_nesting = cognitive.get('max_nesting', 0)
        if max_nesting > 6:
            score -= 40  # Deeply nested (increased from 30)
        elif max_nesting > 5:
            score -= 30  # Increased from 20
        elif max_nesting > 3:
            score -= 20  # Increased from 12
        elif max_nesting > 2:
            score -= 10  # Increased from 6
        elif max_nesting > 1:
            score -= 5   # Even nesting of 2 gets penalized
        
        return max(0, score)
    
    def _calculate_security_score(self, security_analysis: Dict) -> float:
        """Calculate security score"""
        if not security_analysis:
            return 100.0
        
        return security_analysis.get('score', 100.0)
    
    def _calculate_documentation_score(self, smells: List, auto_fix_report: Dict) -> float:
        """Calculate documentation score"""
        score = 100.0
        
        # More aggressive penalties for missing docstrings
        if auto_fix_report:
            docstring_issues = len([f for f in auto_fix_report.get('fixes', []) 
                                   if f.get('type') == 'docstring'])
            score -= docstring_issues * 15  # Increased from 5 - docstrings are critical
        
        # Check for excessive comments (code smell)
        comment_issues = [s for s in smells if hasattr(s, 'kind') and 
                         s.kind == 'excessive_comments']
        score -= len(comment_issues) * 8  # Increased from 3
        
        # Check for TODO comments (indicates incomplete work)
        todo_issues = [s for s in smells if hasattr(s, 'kind') and 
                      s.kind == 'todo_comment']
        score -= len(todo_issues) * 5  # New: penalize TODOs
        
        return max(0, score)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(
        self,
        style: float,
        maintainability: float,
        complexity: float,
        security: float,
        documentation: float
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if style < 70:
            recommendations.append("📝 Improve code style - run auto-formatter (PEP8)")
        if maintainability < 70:
            recommendations.append("🔧 Reduce code complexity - break down large functions")
        if complexity < 70:
            recommendations.append("📊 Simplify logic - reduce nesting and cyclomatic complexity")
        if security < 80:
            recommendations.append("🔒 Fix security issues - review and address vulnerabilities")
        if documentation < 70:
            recommendations.append("📚 Add documentation - write docstrings for functions and classes")
        
        if not recommendations:
            recommendations.append("✨ Excellent code quality - keep it up!")
        
        return recommendations
