"""
Syntax analyzer for GLSL code
"""
from typing import Dict, Any, List
import re

class SyntaxAnalyzer:
    """Analyzes GLSL syntax"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyze GLSL syntax"""
        self.errors = []
        self.warnings = []
        
        # Check for basic syntax issues
        self._check_braces(code)
        self._check_semicolons(code)
        self._check_parentheses(code)
        self._check_comments(code)
        
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "syntax_score": self._calculate_syntax_score()
        }
    
    def _check_braces(self, code: str):
        """Check for balanced braces"""
        brace_stack = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for char_num, char in enumerate(line, 1):
                if char == '{':
                    brace_stack.append(('{', line_num, char_num))
                elif char == '}':
                    if not brace_stack or brace_stack[-1][0] != '{':
                        self.errors.append({
                            "message": "Unmatched closing brace",
                            "line": line_num,
                            "column": char_num,
                            "severity": "error"
                        })
                    else:
                        brace_stack.pop()
        
        # Check for unclosed braces
        for brace, line_num, char_num in brace_stack:
            self.errors.append({
                "message": f"Unclosed {brace}",
                "line": line_num,
                "column": char_num,
                "severity": "error"
            })
    
    def _check_semicolons(self, code: str):
        """Check for missing semicolons"""
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if (stripped and not stripped.endswith(';') and 
                not stripped.endswith('{') and not stripped.endswith('}') and
                not stripped.startswith('#') and not stripped.startswith('//') and
                not stripped.startswith('/*') and not stripped.startswith('*') and
                not stripped.startswith('if') and not stripped.startswith('for') and
                not stripped.startswith('while') and not stripped.startswith('else')):
                self.warnings.append({
                    "message": "Possible missing semicolon",
                    "line": line_num,
                    "column": len(line),
                    "severity": "warning"
                })
    
    def _check_parentheses(self, code: str):
        """Check for balanced parentheses"""
        paren_stack = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for char_num, char in enumerate(line, 1):
                if char == '(':
                    paren_stack.append(('(', line_num, char_num))
                elif char == ')':
                    if not paren_stack or paren_stack[-1][0] != '(':
                        self.errors.append({
                            "message": "Unmatched closing parenthesis",
                            "line": line_num,
                            "column": char_num,
                            "severity": "error"
                        })
                    else:
                        paren_stack.pop()
        
        # Check for unclosed parentheses
        for paren, line_num, char_num in paren_stack:
            self.errors.append({
                "message": f"Unclosed {paren}",
                "line": line_num,
                "column": char_num,
                "severity": "error"
            })
    
    def _check_comments(self, code: str):
        """Check for comment issues"""
        # Check for unclosed block comments
        if code.count('/*') != code.count('*/'):
            self.warnings.append({
                "message": "Possible unclosed block comment",
                "line": 1,
                "column": 1,
                "severity": "warning"
            })
    
    def _calculate_syntax_score(self) -> float:
        """Calculate syntax score (0-100)"""
        if not self.errors and not self.warnings:
            return 100.0
        
        # Simple scoring: deduct points for errors and warnings
        error_penalty = len(self.errors) * 10
        warning_penalty = len(self.warnings) * 2
        
        score = max(0, 100 - error_penalty - warning_penalty)
        return score 