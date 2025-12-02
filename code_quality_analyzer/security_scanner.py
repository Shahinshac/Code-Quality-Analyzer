"""
Security Vulnerability Scanner using Bandit
Detects security issues in Python code
"""
import subprocess
import tempfile
import os
import json
from typing import Dict, List


class SecurityScanner:
    """Scan code for security vulnerabilities"""
    
    def __init__(self):
        self.severity_levels = ['LOW', 'MEDIUM', 'HIGH']
    
    def scan(self, code: str) -> Dict:
        """Scan code for security vulnerabilities using Bandit"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            try:
                # Run bandit with aggressive settings
                result = subprocess.run(
                    ['bandit', '-f', 'json', '-ll', '-c', 'bandit.yaml', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    errors='ignore'
                )
                
                # Parse JSON output
                vulnerabilities = []
                if result.stdout:
                    try:
                        bandit_data = json.loads(result.stdout)
                        vulnerabilities = self._parse_bandit_output(bandit_data)
                    except:
                        pass
                
                # Add custom security checks
                custom_checks = self._custom_security_checks(code)
                
                return {
                    'vulnerabilities': vulnerabilities + custom_checks,
                    'summary': self._generate_summary(vulnerabilities + custom_checks),
                    'score': self._calculate_security_score(vulnerabilities + custom_checks)
                }
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            # Still run custom checks even if Bandit fails
            try:
                custom_checks = self._custom_security_checks(code)
                return {
                    'vulnerabilities': custom_checks,
                    'summary': self._generate_summary(custom_checks),
                    'score': self._calculate_security_score(custom_checks),
                    'error': f'Bandit scan failed, using custom checks only: {str(e)}'
                }
            except:
                return {
                    'vulnerabilities': [],
                    'summary': {'total': 0, 'high': 0, 'medium': 0, 'low': 0},
                    'score': 100,
                    'error': str(e)
                }
    
    def _parse_bandit_output(self, bandit_data: Dict) -> List[Dict]:
        """Parse Bandit JSON output"""
        vulnerabilities = []
        
        for result in bandit_data.get('results', []):
            vulnerabilities.append({
                'type': 'bandit',
                'test_id': result.get('test_id', ''),
                'test_name': result.get('test_name', ''),
                'severity': result.get('issue_severity', 'MEDIUM'),
                'confidence': result.get('issue_confidence', 'MEDIUM'),
                'line': result.get('line_number', 0),
                'message': result.get('issue_text', ''),
                'code': result.get('code', '').strip(),
                'cwe': result.get('issue_cwe', {})
            })
        
        return vulnerabilities
    
    def _custom_security_checks(self, code: str) -> List[Dict]:
        """Custom security pattern matching"""
        import re
        vulnerabilities = []
        lines = code.split('\n')
        
        # Check for hardcoded passwords/secrets (more patterns)
        password_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded Password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API Key'),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded Secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded Token'),
            (r'auth[_-]?token\s*=\s*["\'][^"\']+["\']', 'Hardcoded Auth Token'),
            (r'access[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded Access Key'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, name in password_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append({
                        'type': 'custom',
                        'test_id': 'HARDCODED_SECRET',
                        'test_name': name,
                        'severity': 'HIGH',
                        'confidence': 'HIGH',
                        'line': i,
                        'message': f'{name} detected - never hardcode credentials',
                        'code': line.strip()
                    })
        
        # Check for eval/exec usage
        if 'eval(' in code or 'exec(' in code:
            for i, line in enumerate(lines, 1):
                if 'eval(' in line or 'exec(' in line:
                    vulnerabilities.append({
                        'type': 'custom',
                        'test_id': 'DANGEROUS_EVAL',
                        'test_name': 'Dangerous Function',
                        'severity': 'HIGH',
                        'confidence': 'HIGH',
                        'line': i,
                        'message': 'Use of eval() or exec() is dangerous',
                        'code': line.strip()
                    })
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'execute\(["\'].*%s.*["\'].*%',
            r'execute\(["\'].*\+.*["\']',
            r'execute\(f["\'].*{.*}.*["\']',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in sql_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        'type': 'custom',
                        'test_id': 'SQL_INJECTION',
                        'test_name': 'Possible SQL Injection',
                        'severity': 'HIGH',
                        'confidence': 'MEDIUM',
                        'line': i,
                        'message': 'Possible SQL injection vulnerability',
                        'code': line.strip()
                    })
        
        # Check for unsafe subprocess usage
        if 'subprocess' in code and 'shell=True' in code:
            for i, line in enumerate(lines, 1):
                if 'shell=True' in line:
                    vulnerabilities.append({
                        'type': 'custom',
                        'test_id': 'UNSAFE_SUBPROCESS',
                        'test_name': 'Unsafe Subprocess',
                        'severity': 'MEDIUM',
                        'confidence': 'HIGH',
                        'line': i,
                        'message': 'Using shell=True with subprocess is risky',
                        'code': line.strip()
                    })
        
        return vulnerabilities
    
    def _generate_summary(self, vulnerabilities: List[Dict]) -> Dict:
        """Generate summary statistics"""
        summary = {
            'total': len(vulnerabilities),
            'high': 0,
            'medium': 0,
            'low': 0,
            'by_type': {}
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'MEDIUM').upper()
            if severity == 'HIGH':
                summary['high'] += 1
            elif severity == 'MEDIUM':
                summary['medium'] += 1
            else:
                summary['low'] += 1
            
            test_name = vuln.get('test_name', 'Unknown')
            summary['by_type'][test_name] = summary['by_type'].get(test_name, 0) + 1
        
        return summary
    
    def _calculate_security_score(self, vulnerabilities: List[Dict]) -> float:
        """Calculate security score (0-100)"""
        if not vulnerabilities:
            return 100.0
        
        # Extremely aggressive penalty points based on severity
        penalties = {
            'HIGH': 30,    # Increased from 25
            'MEDIUM': 18,  # Increased from 15
            'LOW': 10      # Increased from 8
        }
        
        # Extra penalty for eval/exec usage (extremely dangerous)
        eval_exec_penalty = 0
        for vuln in vulnerabilities:
            test_name = vuln.get('test_name', '').lower()
            if 'eval' in test_name or 'exec' in test_name:
                eval_exec_penalty += 15  # Big extra penalty
        
        total_penalty = eval_exec_penalty
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'MEDIUM').upper()
            total_penalty += penalties.get(severity, 10)
        
        score = max(0, 100 - total_penalty)
        return round(score, 2)
