from code_quality_analyzer.detectors import RuleBasedDetector


def test_detect_java_long_method():
    java_src = """
    public class Foo {
      public void longMethod() {
        int a = 0;
        int b = 1;
        int c = 2;
        int d = 3;
        int e = 4;
        int f = 5;
        int g = 6;
        int h = 7;
        int i = 8;
        int j = 9;
      }
    }
    """
    det = RuleBasedDetector()
    smells = det.detect_java_issues(java_src, max_method_length=5)
    kinds = [s.kind for s in smells]
    assert 'java_long_method' in kinds