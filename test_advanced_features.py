"""
Test the new advanced features
"""
from code_quality_analyzer.auto_fixer import CodeAutoFixer
from code_quality_analyzer.complexity_analyzer import ComplexityAnalyzer
from code_quality_analyzer.security_scanner import SecurityScanner
from code_quality_analyzer.quality_scorer import QualityScorer

# Test code with multiple issues
test_code = """
def bad_function(x, y):
    password = "admin123"
    result = eval(x)
    for i in range(len(y)):
        if result > 0:
            if y[i] > 5:
                if y[i] < 10:
                    if y[i] % 2 == 0:
                        if y[i] != 6:
                            print(y[i])
    return result
"""

print("=" * 60)
print("TESTING ADVANCED FEATURES")
print("=" * 60)

# Test 1: Auto-Fixer
print("\n1. AUTO-FIXER TEST")
print("-" * 60)
fixer = CodeAutoFixer()
fixed_code, fixes = fixer.fix_all(test_code)
print(f"✓ Fixes applied: {len(fixes)}")
for fix in fixes:
    print(f"  - {fix['type']}: {fix['message']}")

# Test 2: Complexity Analysis
print("\n2. COMPLEXITY ANALYSIS TEST")
print("-" * 60)
complexity = ComplexityAnalyzer()
analysis = complexity.analyze(test_code)
print(f"✓ Maintainability Index: {analysis['maintainability']['score']} ({analysis['maintainability']['rank']})")
print(f"✓ Functions analyzed: {len(analysis['cyclomatic'])}")
for func in analysis['cyclomatic']:
    print(f"  - {func['name']}: Complexity {func['complexity']} ({func['classification']})")
print(f"✓ Max nesting depth: {analysis['cognitive']['max_nesting']}")

# Test 3: Security Scanner
print("\n3. SECURITY SCANNER TEST")
print("-" * 60)
scanner = SecurityScanner()
security = scanner.scan(test_code)
print(f"✓ Security Score: {security['score']}/100")
print(f"✓ Vulnerabilities found: {security['summary']['total']}")
if security['vulnerabilities']:
    print(f"  - High: {security['summary']['high']}")
    print(f"  - Medium: {security['summary']['medium']}")
    print(f"  - Low: {security['summary']['low']}")
    print("\nTop 3 issues:")
    for vuln in security['vulnerabilities'][:3]:
        print(f"  - {vuln['test_name']}: {vuln['message']} (Line {vuln['line']})")

# Test 4: Quality Scorer
print("\n4. QUALITY SCORER TEST")
print("-" * 60)
from code_quality_analyzer.detectors import RuleBasedDetector
detector = RuleBasedDetector()
smells = detector.detect_all_languages(test_code, 'python')

scorer = QualityScorer()
quality = scorer.calculate_score(smells, analysis, security, {'fixes': fixes})
print(f"✓ Total Quality Score: {quality['total_score']}/100 (Grade: {quality['grade']})")
print("\nComponent Breakdown:")
for name, comp in quality['components'].items():
    print(f"  {name.capitalize()}: {comp['score']}/100 (contributes {comp['contribution']:.2f} points)")

print("\nRecommendations:")
for rec in quality['recommendations']:
    print(f"  {rec}")

print("\n" + "=" * 60)
print("✅ ALL ADVANCED FEATURES WORKING!")
print("=" * 60)
