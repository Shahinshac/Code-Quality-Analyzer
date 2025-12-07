"""
Universal Security Scanner for Multiple Languages
"""
import re
from typing import Dict, List


class UniversalSecurityScanner:
    SECURITY_PATTERNS = {
        'sql_injection': {
            'pattern': r'(execute|query|exec|prepare)\s*\(\s*["\'].*?\+.*?["\']|string.*?concat|format.*?query',
            'languages': ['python', 'php', 'java', 'csharp', 'javascript', 'typescript'],
            'severity': 'HIGH',
            'message': 'Potential SQL injection vulnerability detected'
        },
        'xss': {
            'pattern': r'innerHTML|document\.write|eval\(|dangerouslySetInnerHTML|<script[^>]*>.*?<\/script>',
            'languages': ['javascript', 'typescript', 'html'],
            'severity': 'HIGH',
            'message': 'Potential XSS vulnerability detected'
        },
        'command_injection': {
            'pattern': r'(system|exec|shell_exec|popen|subprocess|Runtime\.exec)\s*\(',
            'languages': ['python', 'php', 'java', 'ruby'],
            'severity': 'CRITICAL',
            'message': 'Potential command injection vulnerability detected'
        },
        'hardcoded_credentials': {
            'pattern': r'(password|passwd|pwd|secret|api_key|apikey)\s*=\s*["\'][^"\']+["\']',
            'languages': ['python', 'javascript', 'typescript', 'java', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'severity': 'HIGH',
            'message': 'Hardcoded credentials detected'
        },
        'unsafe_eval': {
            'pattern': r'\beval\s*\(',
            'languages': ['python', 'javascript', 'typescript', 'php', 'ruby'],
            'severity': 'HIGH',
            'message': 'Unsafe eval() usage detected'
        },
        'unsafe_deserialize': {
            'pattern': r'(pickle\.loads|yaml\.load|unserialize|JSON\.parse)',
            'languages': ['python', 'php', 'javascript', 'typescript', 'ruby'],
            'severity': 'MEDIUM',
            'message': 'Unsafe deserialization detected'
        },
        'buffer_overflow': {
            'pattern': r'(strcpy|strcat|sprintf|gets)\s*\(',
            'languages': ['cpp', 'c'],
            'severity': 'CRITICAL',
            'message': 'Potential buffer overflow vulnerability'
        },
        'null_pointer': {
            'pattern': r'\.\w+\s*\(.*?\)\s*\.\w+|!\s*\w+\s*&&\s*\w+\.',
            'languages': ['java', 'csharp', 'cpp'],
            'severity': 'MEDIUM',
            'message': 'Potential null pointer dereference'
        }
    }
    
    def __init__(self, language='python'):
        self.language = language.lower()
    
    def scan(self, code):
        vulnerabilities = []
        lines = code.split('\n')
        
        for vuln_type, config in self.SECURITY_PATTERNS.items():
            if self.language in config['languages']:
                for i, line in enumerate(lines, 1):
                    if re.search(config['pattern'], line, re.IGNORECASE):
                        vulnerabilities.append({
                            'line': i,
                            'severity': config['severity'],
                            'test_name': vuln_type.replace('_', ' ').title(),
                            'message': config['message'],
                            'code': line.strip()
                        })
        
        # Calculate security score
        critical = sum(1 for v in vulnerabilities if v['severity'] == 'CRITICAL')
        high = sum(1 for v in vulnerabilities if v['severity'] == 'HIGH')
        medium = sum(1 for v in vulnerabilities if v['severity'] == 'MEDIUM')
        
        score = 100 - (critical * 30) - (high * 15) - (medium * 5)
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'vulnerabilities': vulnerabilities,
            'summary': {
                'total': len(vulnerabilities),
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': 0
            }
        }
