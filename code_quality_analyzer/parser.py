import ast
import astunparse
import re
import os
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class BaseFeatureExtractor(ABC):
    """Base class for language-specific feature extractors"""
    
    @abstractmethod
    def extract_features(self, source: str) -> Dict[str, float]:
        """Extract code metrics from source code"""
        pass


class PythonFeatureExtractor(BaseFeatureExtractor, ast.NodeVisitor):
    """Python-specific feature extractor using AST"""
    
    def __init__(self):
        self.features: Dict[str, int] = {
            "num_functions": 0,
            "avg_function_length": 0,
            "max_function_length": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_assignments": 0,
            "max_nesting": 0,
        }
        self._function_lengths: List[int] = []
        self._current_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.features["num_functions"] += 1
        start_lineno = node.lineno
        end_lineno = getattr(node, 'end_lineno', None)
        if end_lineno is None:
            max_lineno = start_lineno
            for n in ast.walk(node):
                if hasattr(n, 'lineno'):
                    max_lineno = max(max_lineno, n.lineno)
            end_lineno = max_lineno
        length = end_lineno - start_lineno + 1
        self._function_lengths.append(length)
        self.features["max_function_length"] = max(self.features["max_function_length"], length)

        prev_depth = self._current_depth
        self._current_depth = 0
        self.generic_visit(node)
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self._current_depth = prev_depth

    def visit_ClassDef(self, node: ast.ClassDef):
        self.features["num_classes"] += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.features["num_imports"] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.features["num_imports"] += 1
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        self.features["num_assignments"] += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_For(self, node: ast.For):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_While(self, node: ast.While):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_With(self, node: ast.With):
        self._current_depth += 1
        self.features["max_nesting"] = max(self.features["max_nesting"], self._current_depth)
        self.generic_visit(node)
        self._current_depth -= 1

    def extract_features(self, source: str) -> Dict[str, float]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            raise
        self.visit(tree)
        if self._function_lengths:
            self.features["avg_function_length"] = sum(self._function_lengths) / len(self._function_lengths)
        else:
            self.features["avg_function_length"] = 0
        return self.features


class JavaScriptFeatureExtractor(BaseFeatureExtractor):
    """JavaScript/TypeScript feature extractor using regex patterns"""
    
    def extract_features(self, source: str) -> Dict[str, float]:
        features = {
            "num_functions": 0,
            "avg_function_length": 0,
            "max_function_length": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_assignments": 0,
            "max_nesting": 0,
        }
        
        # Count functions (function declarations, arrow functions, methods)
        function_patterns = [
            r'\bfunction\s+\w+\s*\(',
            r'\w+\s*:\s*function\s*\(',
            r'\w+\s*=\s*\([^)]*\)\s*=>',
            r'\w+\s*\([^)]*\)\s*\{',
        ]
        for pattern in function_patterns:
            features["num_functions"] += len(re.findall(pattern, source))
        
        # Count classes
        features["num_classes"] = len(re.findall(r'\bclass\s+\w+', source))
        
        # Count imports
        import_patterns = [r'\bimport\s+', r'\brequire\s*\(']
        for pattern in import_patterns:
            features["num_imports"] += len(re.findall(pattern, source))
        
        # Count assignments
        features["num_assignments"] = len(re.findall(r'\b\w+\s*=\s*', source))
        
        # Estimate nesting depth
        lines = source.split('\n')
        max_nesting = 0
        for line in lines:
            nesting = len(re.findall(r'\{', line)) - len(re.findall(r'\}', line))
            max_nesting = max(max_nesting, nesting)
        features["max_nesting"] = max_nesting
        
        return features


class JavaFeatureExtractor(BaseFeatureExtractor):
    """Java feature extractor using regex patterns"""
    
    def extract_features(self, source: str) -> Dict[str, float]:
        features = {
            "num_functions": 0,
            "avg_function_length": 0,
            "max_function_length": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_assignments": 0,
            "max_nesting": 0,
        }
        
        # Count methods
        method_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{'
        features["num_functions"] = len(re.findall(method_pattern, source))
        
        # Count classes/interfaces
        class_patterns = [r'\bclass\s+\w+', r'\binterface\s+\w+', r'\benum\s+\w+']
        for pattern in class_patterns:
            features["num_classes"] += len(re.findall(pattern, source))
        
        # Count imports
        features["num_imports"] = len(re.findall(r'\bimport\s+', source))
        
        # Count assignments
        features["num_assignments"] = len(re.findall(r'\w+\s*=\s*', source))
        
        # Estimate nesting
        lines = source.split('\n')
        current_depth = 0
        max_nesting = 0
        for line in lines:
            current_depth += line.count('{') - line.count('}')
            max_nesting = max(max_nesting, current_depth)
        features["max_nesting"] = max_nesting
        
        return features


class GenericFeatureExtractor(BaseFeatureExtractor):
    """Generic feature extractor for C++, Go, Rust, Ruby, PHP using patterns"""
    
    def __init__(self, language: str):
        self.language = language
    
    def extract_features(self, source: str) -> Dict[str, float]:
        features = {
            "num_functions": 0,
            "avg_function_length": 0,
            "max_function_length": 0,
            "num_classes": 0,
            "num_imports": 0,
            "num_assignments": 0,
            "max_nesting": 0,
        }
        
        # Language-specific patterns
        patterns = self._get_language_patterns()
        
        for key, pattern_list in patterns.items():
            if isinstance(pattern_list, list):
                for pattern in pattern_list:
                    features[key] += len(re.findall(pattern, source, re.MULTILINE))
            else:
                features[key] = pattern_list(source)
        
        # Estimate nesting
        lines = source.split('\n')
        current_depth = 0
        max_nesting = 0
        for line in lines:
            current_depth += line.count('{') - line.count('}')
            max_nesting = max(max_nesting, current_depth)
        features["max_nesting"] = max_nesting
        
        return features
    
    def _get_language_patterns(self) -> Dict[str, any]:
        """Get language-specific regex patterns"""
        if self.language == 'cpp':
            return {
                "num_functions": [r'\w+\s+\w+\s*\([^)]*\)\s*\{', r'\w+::\w+\s*\([^)]*\)\s*\{'],
                "num_classes": [r'\bclass\s+\w+', r'\bstruct\s+\w+'],
                "num_imports": [r'#include\s*[<"]'],
                "num_assignments": [r'\w+\s*=\s*'],
            }
        elif self.language == 'go':
            return {
                "num_functions": [r'\bfunc\s+\w+\s*\(', r'\bfunc\s+\([^)]+\)\s+\w+\s*\('],
                "num_classes": [r'\btype\s+\w+\s+struct'],
                "num_imports": [r'\bimport\s+'],
                "num_assignments": [r'\w+\s*:=\s*', r'\w+\s*=\s*'],
            }
        elif self.language == 'rust':
            return {
                "num_functions": [r'\bfn\s+\w+\s*\('],
                "num_classes": [r'\bstruct\s+\w+', r'\benum\s+\w+', r'\btrait\s+\w+'],
                "num_imports": [r'\buse\s+'],
                "num_assignments": [r'\blet\s+'],
            }
        elif self.language == 'ruby':
            return {
                "num_functions": [r'\bdef\s+\w+'],
                "num_classes": [r'\bclass\s+\w+', r'\bmodule\s+\w+'],
                "num_imports": [r'\brequire\s+', r'\brequire_relative\s+'],
                "num_assignments": [r'\w+\s*=\s*'],
            }
        elif self.language == 'php':
            return {
                "num_functions": [r'\bfunction\s+\w+\s*\('],
                "num_classes": [r'\bclass\s+\w+', r'\binterface\s+\w+', r'\btrait\s+\w+'],
                "num_imports": [r'\buse\s+', r'\brequire', r'\binclude'],
                "num_assignments": [r'\$\w+\s*=\s*'],
            }
        return {}


def detect_language(filepath: str, source: Optional[str] = None) -> str:
    """Detect programming language from file extension"""
    ext = os.path.splitext(filepath)[1].lower()
    
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'cpp',
        '.h': 'cpp',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
    }
    
    return ext_map.get(ext, 'unknown')


def get_feature_extractor(language: str) -> Optional[BaseFeatureExtractor]:
    """Get appropriate feature extractor for the language"""
    extractors = {
        'python': PythonFeatureExtractor,
        'javascript': JavaScriptFeatureExtractor,
        'typescript': JavaScriptFeatureExtractor,
        'java': JavaFeatureExtractor,
        'cpp': lambda: GenericFeatureExtractor('cpp'),
        'go': lambda: GenericFeatureExtractor('go'),
        'rust': lambda: GenericFeatureExtractor('rust'),
        'ruby': lambda: GenericFeatureExtractor('ruby'),
        'php': lambda: GenericFeatureExtractor('php'),
    }
    
    extractor_class = extractors.get(language)
    return extractor_class() if extractor_class else None


# Legacy alias for backwards compatibility
ASTFeatureExtractor = PythonFeatureExtractor


def extract_features_from_file(path: str) -> Dict[str, float]:
    """Extract features from a source file with automatic language detection"""
    with open(path, 'r', encoding='utf8') as fh:
        src = fh.read()
    
    language = detect_language(path, src)
    extractor = get_feature_extractor(language)
    
    if not extractor:
        raise ValueError(f"Unsupported language: {language}")
    
    return extractor.extract_features(src)


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    feat = extract_features_from_file(path)
    print(f"Language: {detect_language(path)}")
    print(feat)
