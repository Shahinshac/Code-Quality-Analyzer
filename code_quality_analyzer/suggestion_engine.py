from typing import List
from .detectors import CodeSmell


def suggestions_for_smell(smell: CodeSmell) -> List[str]:
    if smell.kind == 'long_function':
        return [
            'Consider splitting this function into smaller functions with single responsibility.',
            'Move some logic into helper functions or a new class.'
        ]
    if smell.kind == 'deep_nesting':
        return [
            'Reduce nesting by early returns or by extracting nested blocks into functions.',
        ]
    if smell.kind == 'unused_import':
        return [
            'Remove the unused import to keep the code clean.',
        ]
    if smell.kind == 'unused_variable':
        return [
            'Remove the unused variable or use it appropriately.',
        ]
    return ['No suggestion available']


def suggestions_for_smells(smells: List[CodeSmell]):
    results = []
    for s in smells:
        results.append({
            'smell': s.to_dict(),
            'suggestions': suggestions_for_smell(s)
        })
    return results
