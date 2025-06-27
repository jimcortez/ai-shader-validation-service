"""
Semantic analyzer for GLSL code
"""
from typing import Dict, Any, List, Set
import re

class SemanticAnalyzer:
    """Analyzes GLSL semantics"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.declared_variables: Set[str] = set()
        self.declared_functions: Set[str] = set()
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyze GLSL semantics"""
        self.errors = []
        self.warnings = []
        self.info = []
        self.declared_variables.clear()
        self.declared_functions.clear()
        
        # Extract declarations
        self._extract_declarations(code)
        
        # Check for semantic issues
        self._check_undefined_variables(code)
        self._check_undefined_functions(code)
        self._check_type_compatibility(code)
        self._check_builtin_variables(code)
        
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "declared_variables": list(self.declared_variables),
            "declared_functions": list(self.declared_functions),
            "semantic_score": self._calculate_semantic_score()
        }
    
    def _extract_declarations(self, code: str):
        """Extract variable and function declarations"""
        # Extract variable declarations
        var_patterns = [
            r'uniform\s+(\w+)\s+(\w+)',
            r'attribute\s+(\w+)\s+(\w+)',
            r'varying\s+(\w+)\s+(\w+)',
            r'(\w+)\s+(\w+)\s*;',  # Simple variable declarations
        ]
        
        for pattern in var_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                var_name = match.group(2)
                self.declared_variables.add(var_name)
        
        # Extract function declarations
        func_pattern = r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.finditer(func_pattern, code)
        for match in matches:
            func_name = match.group(2)
            self.declared_functions.add(func_name)
    
    def _check_undefined_variables(self, code: str):
        """Check for undefined variables"""
        # Find all variable usages
        var_usage_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.finditer(var_usage_pattern, code)
        
        for match in matches:
            var_name = match.group(1)
            
            # Skip keywords and built-in functions
            if self._is_keyword(var_name) or self._is_builtin_function(var_name):
                continue
            
            # Check if variable is declared
            if var_name not in self.declared_variables:
                self.errors.append({
                    "message": f"Undefined variable: {var_name}",
                    "line": 1,  # Would need line tracking in full implementation
                    "column": match.start(),
                    "severity": "error"
                })
    
    def _check_undefined_functions(self, code: str):
        """Check for undefined functions"""
        # Find function calls
        func_call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.finditer(func_call_pattern, code)
        
        for match in matches:
            func_name = match.group(1)
            
            # Skip built-in functions
            if self._is_builtin_function(func_name):
                continue
            
            # Check if function is declared
            if func_name not in self.declared_functions:
                self.warnings.append({
                    "message": f"Undefined function: {func_name}",
                    "line": 1,  # Would need line tracking in full implementation
                    "column": match.start(),
                    "severity": "warning"
                })
    
    def _check_type_compatibility(self, code: str):
        """Check for type compatibility issues"""
        # Check for obvious type mismatches
        type_mismatches = [
            (r'float\s+\w+\s*=\s*"', 'String assigned to float'),
            (r'int\s+\w+\s*=\s*"', 'String assigned to int'),
            (r'bool\s+\w+\s*=\s*"', 'String assigned to bool'),
        ]
        
        for pattern, message in type_mismatches:
            if re.search(pattern, code):
                self.errors.append({
                    "message": message,
                    "line": 1,
                    "column": 1,
                    "severity": "error"
                })
    
    def _check_builtin_variables(self, code: str):
        """Check for proper use of built-in variables"""
        # Check for fragment shader output
        if 'gl_FragColor' in code and 'gl_Position' not in code:
            self.info.append({
                "message": "Fragment shader detected (uses gl_FragColor)",
                "line": 1,
                "column": 1,
                "severity": "info"
            })
        
        # Check for vertex shader output
        if 'gl_Position' in code and 'gl_FragColor' not in code:
            self.info.append({
                "message": "Vertex shader detected (uses gl_Position)",
                "line": 1,
                "column": 1,
                "severity": "info"
            })
    
    def _is_keyword(self, word: str) -> bool:
        """Check if word is a GLSL keyword"""
        keywords = {
            'void', 'bool', 'int', 'uint', 'float', 'double',
            'vec2', 'vec3', 'vec4', 'mat2', 'mat3', 'mat4',
            'sampler2D', 'samplerCube', 'uniform', 'attribute',
            'varying', 'const', 'in', 'out', 'inout',
            'if', 'else', 'for', 'while', 'do', 'break',
            'continue', 'return', 'discard'
        }
        return word in keywords
    
    def _is_builtin_function(self, word: str) -> bool:
        """Check if word is a built-in GLSL function"""
        builtin_functions = {
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'pow', 'exp', 'log', 'sqrt', 'abs', 'sign',
            'floor', 'ceil', 'fract', 'mod', 'min', 'max',
            'clamp', 'mix', 'step', 'smoothstep', 'length',
            'distance', 'dot', 'cross', 'normalize', 'reflect',
            'refract', 'texture2D', 'textureCube'
        }
        return word in builtin_functions
    
    def _calculate_semantic_score(self) -> float:
        """Calculate semantic score (0-100)"""
        if not self.errors and not self.warnings:
            return 100.0
        
        # Simple scoring: deduct points for errors and warnings
        error_penalty = len(self.errors) * 15
        warning_penalty = len(self.warnings) * 3
        
        score = max(0, 100 - error_penalty - warning_penalty)
        return score 