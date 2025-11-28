import os
from code_quality_analyzer.parser import extract_features_from_file


def test_parser_basic():
    this_dir = os.path.dirname(__file__)
    good = os.path.join(this_dir, '..', 'examples', 'good_example.py')
    feats = extract_features_from_file(good)
    assert feats['num_functions'] >= 1
    assert feats['num_imports'] >= 1


def test_parser_bad():
    this_dir = os.path.dirname(__file__)
    bad = os.path.join(this_dir, '..', 'examples', 'bad_example.py')
    feats = extract_features_from_file(bad)
    assert feats['max_function_length'] > 20
    assert feats['max_nesting'] >= 4
