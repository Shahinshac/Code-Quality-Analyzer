"""Test accuracy of code quality detection"""

from code_quality_analyzer.detectors import RuleBasedDetector
from code_quality_analyzer.quality_scorer import QualityScorer
from code_quality_analyzer.complexity_analyzer import ComplexityAnalyzer
from code_quality_analyzer.security_scanner import SecurityScanner
from code_quality_analyzer.auto_fixer import CodeAutoFixer

# GOOD CODE - Should get high score (90+)
good_code = """
def calculate_average(numbers: list) -> float:
    \"\"\"Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numeric values
        
    Returns:
        float: The average value
    \"\"\"
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def process_items(items: list, threshold: int) -> list:
    \"\"\"Process items above a threshold.
    
    Args:
        items: List of items to process
        threshold: Minimum value threshold
        
    Returns:
        list: Filtered items
    \"\"\"
    return [item for item in items if item > threshold]
"""

# BAD CODE - Should get low score (30-50)
bad_code = """
def x(a,b):
    password='admin123'
    api_key='sk-1234567890'
    c=eval(a)
    d=exec('import os')
    for i in range(len(b)):
        if c>0:
            if b[i]>5:
                if b[i]<10:
                    if b[i]%2==0:
                        if b[i]!=6:
                            if b[i]!=8:
                                if True:
                                    print(b[i])
    # This is a comment
    # This is another comment
    # Too many comments
    # More comments
    # Even more comments
    query = "SELECT * FROM users WHERE id = " + str(a)
    return c
"""

def test_code(code, label):
    print(f"\n{'='*70}")
    print(f"{label}")
    print('='*70)
    
    detector = RuleBasedDetector()
    smells = detector.detect_all_languages(code, 'python')
    
    complexity = ComplexityAnalyzer().analyze(code)
    security = SecurityScanner().scan(code)
    fixer = CodeAutoFixer()
    _, fixes = fixer.fix_all(code)
    
    scorer = QualityScorer()
    quality = scorer.calculate_score(
        smells, 
        complexity, 
        security,
        {'fixes': fixes}
    )
    
    print(f"\n📊 OVERALL SCORE: {quality['total_score']}/100 (Grade: {quality['grade']})")
    print(f"\n🔍 Detection Results:")
    print(f"   Code Smells: {len(smells)}")
    print(f"   Security Issues: {len(security['vulnerabilities'])}")
    print(f"   Auto-fixes Available: {len(fixes)}")
    
    print(f"\n📈 Component Scores:")
    for name, comp in quality['components'].items():
        print(f"   {name.capitalize():15s}: {comp['score']:6.2f}/100 (weight: {comp['weight']}%)")
    
    if security['vulnerabilities']:
        print(f"\n🔒 Security Issues:")
        for vuln in security['vulnerabilities'][:5]:
            print(f"   - {vuln['test_name']}: {vuln['message']}")
    
    if complexity.get('cyclomatic'):
        print(f"\n📊 Complexity:")
        for func in complexity['cyclomatic']:
            print(f"   - {func['name']}: Complexity {func['complexity']} ({func['classification']})")
    
    print(f"\n💡 Recommendations:")
    for rec in quality['recommendations'][:3]:
        print(f"   {rec}")
    
    return quality['total_score'], quality['grade']

# Run tests
good_score, good_grade = test_code(good_code, "✅ GOOD CODE TEST")
bad_score, bad_grade = test_code(bad_code, "❌ BAD CODE TEST")

print(f"\n{'='*70}")
print("ACCURACY SUMMARY")
print('='*70)
print(f"Good Code: {good_score}/100 (Grade: {good_grade}) - Expected: 85-100")
print(f"Bad Code:  {bad_score}/100 (Grade: {bad_grade}) - Expected: 20-60")

if good_score >= 85 and bad_score <= 60:
    print("\n✅ ACCURACY TEST PASSED!")
    score_diff = good_score - bad_score
    print(f"Score difference: {score_diff} points")
else:
    print("\n❌ ACCURACY NEEDS IMPROVEMENT!")
    if good_score < 85:
        print(f"   Good code score too low: {good_score} (should be >= 85)")
    if bad_score > 60:
        print(f"   Bad code score too high: {bad_score} (should be <= 60)")
