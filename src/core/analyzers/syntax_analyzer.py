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
            
            # Skip empty lines, comments, and control structures
            if (not stripped or 
                stripped.startswith('#') or 
                stripped.startswith('//') or 
                stripped.startswith('/*') or 
                stripped.startswith('*') or
                stripped.endswith('{') or 
                stripped.endswith('}') or
                stripped.startswith('if') or 
                stripped.startswith('for') or
                stripped.startswith('while') or 
                stripped.startswith('else') or
                stripped.startswith('void') or
                stripped.startswith('uniform') or
                stripped.startswith('attribute') or
                stripped.startswith('varying') or
                stripped.startswith('in') or
                stripped.startswith('out')):
                continue
            
            # Check for statements that should end with semicolon
            # Look for assignment statements, function calls, etc.
            if (('=' in stripped and not stripped.endswith(';')) or
                ('(' in stripped and ')' in stripped and not stripped.endswith(';') and not stripped.endswith('{')) or
                (any(keyword in stripped for keyword in ['vec4', 'vec3', 'vec2', 'float', 'int', 'bool']) and 
                 '=' in stripped and not stripped.endswith(';'))):
                
                # Additional check: if line ends with a comment, check if the statement before it ends with semicolon
                if '//' in stripped:
                    statement_part = stripped.split('//')[0].strip()
                    if statement_part and not statement_part.endswith(';'):
                        self.errors.append({
                            "message": "Missing semicolon at end of statement",
                            "line": line_num,
                            "column": len(line),
                            "severity": "error"
                        })
                else:
                    self.errors.append({
                        "message": "Missing semicolon at end of statement",
                        "line": line_num,
                        "column": len(line),
                        "severity": "error"
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