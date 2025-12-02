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
            'style': 25,           # PEP8 compliance
            'maintainability': 25,  # Maintainability index
            'complexity': 20,       # Cyclomatic/cognitive complexity
            'security': 20,         # Security vulnerabilities
            'documentation': 10     # Docstrings and comments
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
                       s.kind in ['long_line', 'trailing_whitespace', 'naming']]
        
        penalty = len(style_issues) * 3
        if auto_fix_report:
            pep8_fixes = len([f for f in auto_fix_report.get('fixes', []) 
                            if f.get('type') == 'pep8'])
            penalty += pep8_fixes * 2
        
        return max(0, 100 - penalty)
    
    def _calculate_maintainability_score(self, complexity_analysis: Dict) -> float:
        """Calculate maintainability score"""
        if not complexity_analysis:
            return 75.0  # Default score
        
        mi_data = complexity_analysis.get('maintainability', {})
        return mi_data.get('score', 75.0)
    
    def _calculate_complexity_score(self, complexity_analysis: Dict) -> float:
        """Calculate complexity score"""
        if not complexity_analysis:
            return 75.0
        
        score = 100.0
        
        # Cyclomatic complexity penalty
        cyclomatic = complexity_analysis.get('cyclomatic', [])
        for item in cyclomatic:
            if item['complexity'] > 10:
                score -= 5
            elif item['complexity'] > 5:
                score -= 2
        
        # Cognitive complexity penalty
        cognitive = complexity_analysis.get('cognitive', {})
        max_nesting = cognitive.get('max_nesting', 0)
        if max_nesting > 5:
            score -= 10
        elif max_nesting > 3:
            score -= 5
        
        return max(0, score)
    
    def _calculate_security_score(self, security_analysis: Dict) -> float:
        """Calculate security score"""
        if not security_analysis:
            return 100.0
        
        return security_analysis.get('score', 100.0)
    
    def _calculate_documentation_score(self, smells: List, auto_fix_report: Dict) -> float:
        """Calculate documentation score"""
        score = 100.0
        
        # Check for missing docstrings
        if auto_fix_report:
            docstring_issues = len([f for f in auto_fix_report.get('fixes', []) 
                                   if f.get('type') == 'docstring'])
            score -= docstring_issues * 5
        
        # Check for excessive comments
        comment_issues = [s for s in smells if hasattr(s, 'kind') and 
                         s.kind == 'excessive_comments']
        score -= len(comment_issues) * 3
        
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
