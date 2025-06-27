"""
GLSL parser implementation
"""
from typing import Dict, Any, Optional, List
from src.core.parser.base_parser import BaseShaderParser
from src.core.parser.glsl_lexer import GLSLLexer
from src.core.parser.glsl_ast import *
import re

class GLSLParser(BaseShaderParser):
    """GLSL parser implementation"""
    
    def __init__(self, code: str, parameters: Optional[Dict[str, Any]] = None):
        super().__init__(code, parameters)
        self.lexer = GLSLLexer()
        self.errors = []
        self.warnings = []
        self.info = []
    
    def parse(self) -> Any:
        """Parse GLSL code and return AST"""
        try:
            # For now, return a simple representation
            # In a full implementation, this would use the lexer and build a proper AST
            return self._simple_parse()
        except Exception as e:
            self.errors.append({
                "message": f"Parse error: {str(e)}",
                "severity": "error",
                "line": 1,
                "column": 1
            })
            return None
    
    def validate(self) -> Dict[str, Any]:
        """Perform syntax and semantic validation"""
        validation_result = {
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }
        
        # Basic syntax validation
        self._validate_syntax()
        
        # Semantic validation
        self._validate_semantics()
        
        return validation_result
    
    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata from GLSL code"""
        metadata = {
            "version": self._detect_version(),
            "uniforms": self._extract_uniforms(),
            "attributes": self._extract_attributes(),
            "varyings": self._extract_varyings(),
            "functions": self._extract_functions()
        }
        return metadata
    
    def _simple_parse(self) -> Dict[str, Any]:
        """Simple parsing for demonstration"""
        lines = self.code.split('\n')
        return {
            "type": "glsl_program",
            "lines": len(lines),
            "characters": len(self.code)
        }
    
    def _validate_syntax(self):
        """Basic syntax validation"""
        # Check for basic GLSL structure
        if not self.code.strip():
            self.errors.append({
                "message": "Empty shader code",
                "severity": "error",
                "line": 1,
                "column": 1
            })
            return
        
        # Check for version directive
        if not re.search(r'#version\s+\d+', self.code):
            self.warnings.append({
                "message": "No version directive found",
                "severity": "warning",
                "line": 1,
                "column": 1
            })
        
        # Check for basic GLSL keywords
        required_keywords = ['void', 'main']
        for keyword in required_keywords:
            if keyword not in self.code:
                self.errors.append({
                    "message": f"Missing required keyword: {keyword}",
                    "severity": "error",
                    "line": 1,
                    "column": 1
                })
        
        # Check for missing semicolons
        self._check_missing_semicolons()
        
        # Check for unmatched braces
        self._check_unmatched_braces()
        
        # Check for incomplete statements
        self._check_incomplete_statements()
    
    def _check_missing_semicolons(self):
        """Check for missing semicolons after statements"""
        lines = self.code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Skip empty lines, comments, and control structures
            if (not stripped_line or 
                stripped_line.startswith('//') or 
                stripped_line.startswith('/*') or
                stripped_line.startswith('#') or
                stripped_line.endswith('{') or
                stripped_line.endswith('}') or
                'if' in stripped_line or
                'for' in stripped_line or
                'while' in stripped_line or
                'return' in stripped_line):
                continue
            
            # Check for variable declarations and assignments that should end with semicolon
            if (re.search(r'\b(?:uniform|attribute|varying|in|out|const)\s+\w+\s+\w+', stripped_line) or
                re.search(r'\w+\s*=\s*[^;]+$', stripped_line) or
                re.search(r'\w+\s*\([^)]*\)\s*$', stripped_line)):  # Function calls
                
                if not stripped_line.endswith(';'):
                    self.errors.append({
                        "message": "Missing semicolon",
                        "severity": "error",
                        "line": line_num,
                        "column": len(stripped_line) + 1
                    })
    
    def _check_unmatched_braces(self):
        """Check for unmatched braces"""
        open_braces = 0
        lines = self.code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for char_num, char in enumerate(line, 1):
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                    if open_braces < 0:
                        self.errors.append({
                            "message": "Unmatched closing brace",
                            "severity": "error",
                            "line": line_num,
                            "column": char_num
                        })
        
        if open_braces > 0:
            self.errors.append({
                "message": f"Unmatched opening brace(s): {open_braces}",
                "severity": "error",
                "line": len(lines),
                "column": 1
            })
    
    def _check_incomplete_statements(self):
        """Check for incomplete statements"""
        lines = self.code.split('\n')
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Check for incomplete function calls
            if re.search(r'\w+\s*\([^)]*$', stripped_line):
                self.errors.append({
                    "message": "Incomplete function call - missing closing parenthesis",
                    "severity": "error",
                    "line": line_num,
                    "column": len(stripped_line) + 1
                })
            
            # Check for incomplete string literals
            if stripped_line.count('"') % 2 != 0:
                self.errors.append({
                    "message": "Unmatched string literal",
                    "severity": "error",
                    "line": line_num,
                    "column": stripped_line.find('"') + 1
                })
    
    def _validate_semantics(self):
        """Basic semantic validation"""
        # Check for undefined variables
        self._check_undefined_variables()
        
        # Check for type mismatches
        self._check_type_mismatches()
    
    def _check_undefined_variables(self):
        """Check for undefined variables"""
        # Simple check for common undefined variables
        undefined_patterns = [
            r'\bgl_FragColor\b',  # Should be defined in fragment shaders
            r'\bgl_Position\b',   # Should be defined in vertex shaders
        ]
        
        for pattern in undefined_patterns:
            if re.search(pattern, self.code):
                self.info.append({
                    "message": f"Using built-in variable: {pattern}",
                    "severity": "info",
                    "line": 1,
                    "column": 1
                })
    
    def _check_type_mismatches(self):
        """Check for type mismatches"""
        # Simple type mismatch checks
        type_mismatches = [
            (r'float\s+\w+\s*=\s*"', 'String assigned to float'),
            (r'int\s+\w+\s*=\s*"', 'String assigned to int'),
        ]
        
        for pattern, message in type_mismatches:
            if re.search(pattern, self.code):
                self.errors.append({
                    "message": message,
                    "severity": "error",
                    "line": 1,
                    "column": 1
                })
    
    def _detect_version(self) -> str:
        """Detect GLSL version"""
        version_match = re.search(r'#version\s+(\d+)', self.code)
        if version_match:
            return version_match.group(1)
        return "unknown"
    
    def _extract_uniforms(self) -> List[Dict[str, Any]]:
        """Extract uniform declarations"""
        uniforms = []
        uniform_pattern = r'uniform\s+(\w+)\s+(\w+)\s*;'
        matches = re.finditer(uniform_pattern, self.code)
        
        for match in matches:
            uniforms.append({
                "type": match.group(1),
                "name": match.group(2)
            })
        
        return uniforms
    
    def _extract_attributes(self) -> List[Dict[str, Any]]:
        """Extract attribute declarations"""
        attributes = []
        attribute_pattern = r'attribute\s+(\w+)\s+(\w+)\s*;'
        matches = re.finditer(attribute_pattern, self.code)
        
        for match in matches:
            attributes.append({
                "type": match.group(1),
                "name": match.group(2)
            })
        
        return attributes
    
    def _extract_varyings(self) -> List[Dict[str, Any]]:
        """Extract varying declarations"""
        varyings = []
        varying_pattern = r'varying\s+(\w+)\s+(\w+)\s*;'
        matches = re.finditer(varying_pattern, self.code)
        
        for match in matches:
            varyings.append({
                "type": match.group(1),
                "name": match.group(2)
            })
        
        return varyings
    
    def _extract_functions(self) -> List[Dict[str, Any]]:
        """Extract function declarations"""
        functions = []
        function_pattern = r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.finditer(function_pattern, self.code)
        
        for match in matches:
            functions.append({
                "return_type": match.group(1),
                "name": match.group(2)
            })
        
        return functions 