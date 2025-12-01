from typing import List
from .detectors import CodeSmell


def suggestions_for_smell(smell: CodeSmell) -> List[str]:
    """Generate suggestions for a code smell"""
    kind = smell.kind if hasattr(smell, 'kind') else smell.get('kind', '')
    
    if kind == 'long_function':
        return [
            'Consider splitting this function into smaller functions with single responsibility.',
            'Move some logic into helper functions or a new class.'
        ]
    if kind == 'deep_nesting':
        return [
            'Reduce nesting by early returns or by extracting nested blocks into functions.',
        ]
    if kind == 'unused_import':
        return [
            'Remove the unused import to keep the code clean.',
        ]
    if kind == 'unused_variable':
        return [
            'Remove the unused variable or use it appropriately.',
        ]
    if 'flake8' in kind or 'pylint' in kind:
        return [
            'Follow the linter recommendation to improve code quality.',
        ]
    if 'java' in kind:
        return [
            'Refactor this Java code to improve maintainability.',
        ]
    return ['Review and refactor this code section']


def suggestions_for_smells(smells: List[CodeSmell]):
    """Generate suggestions for a list of code smells"""
    results = []
    for s in smells:
        smell_dict = s.to_dict() if hasattr(s, 'to_dict') else s
        results.append({
            'smell': smell_dict,
            'suggestions': suggestions_for_smell(s)
        })
    return results
