import os
from code_quality_analyzer.detectors import RuleBasedDetector


def test_detect_long_and_nesting():
    this_dir = os.path.dirname(__file__)
    bad = os.path.join(this_dir, '..', 'examples', 'bad_example.py')
    with open(bad, 'r', encoding='utf8') as fh:
        src = fh.read()
    det = RuleBasedDetector(max_function_length=20, max_nesting=3)
    smells = det.detect_all(src)
    kinds = [s.kind for s in smells]
    assert 'long_function' in kinds
    assert 'deep_nesting' in kinds


def test_detect_unused_imports_and_vars():
    this_dir = os.path.dirname(__file__)
    bad = os.path.join(this_dir, '..', 'examples', 'bad_example.py')
    with open(bad, 'r', encoding='utf8') as fh:
        src = fh.read()
    det = RuleBasedDetector()
    smells = det.detect_all(src)
    kinds = [s.kind for s in smells]
    assert 'unused_variable' in kinds or 'unused_import' in kinds


def test_ml_train_and_predict(tmp_path):
    from code_quality_analyzer.ml_classifier import load_dataset, train_model, load_model, predict_code_quality
    ds = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'synthetic_dataset.csv')
    df = load_dataset(ds)
    model_path = str(tmp_path / 'm.joblib')
    acc = train_model(df, model_path)
    assert acc >= 0.0
    pred, prob = predict_code_quality('def add(a,b):\n    return a + b\n', model_path)
    assert pred in ['good', 'bad']
