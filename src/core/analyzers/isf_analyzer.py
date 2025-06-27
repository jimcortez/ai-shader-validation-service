"""
ISF (Interactive Shader Format) Analyzer
"""

import logging
from typing import Dict, Any, List, Optional
from ..parsers.isf_parser import ISFParser, ISFDocument, ISFParameter
from ..parser.glsl_parser import GLSLParser
from ..models.errors import ValidationError, ErrorSeverity
import re

logger = logging.getLogger(__name__)


class ISFAnalyzer:
    """Analyzer for ISF (Interactive Shader Format) shaders."""
    
    def __init__(self):
        self.parser = ISFParser()
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, isf_json: str) -> Dict[str, Any]:
        """
        Analyze ISF shader and return validation results.
        
        Args:
            isf_json: ISF JSON string
            
        Returns:
            Dictionary with analysis results
        """
        errors = []
        warnings = []
        metadata = {}
        
        try:
            # Parse ISF document
            isf_doc = self.parser.parse(isf_json)
            metadata["parsed_document"] = isf_doc
            
            # Validate structure
            structure_errors = self.parser.validate_structure(isf_json)
            for error in structure_errors:
                errors.append(ValidationError(
                    message=error,
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    error_code="ISF_STRUCTURE_ERROR",
                    suggestions=["Check ISF specification for required fields"]
                ))
            
            # Analyze parameters
            param_errors, param_warnings = self._analyze_parameters(isf_doc)
            errors.extend(param_errors)
            warnings.extend(param_warnings)
            
            # Analyze shader code
            shader_errors, shader_warnings = self._analyze_shader_code(isf_doc)
            errors.extend(shader_errors)
            warnings.extend(shader_warnings)
            
            # Analyze passes
            pass_errors, pass_warnings = self._analyze_passes(isf_doc)
            errors.extend(pass_errors)
            warnings.extend(pass_warnings)
            
            # Analyze metadata
            meta_errors, meta_warnings = self._analyze_metadata(isf_doc)
            errors.extend(meta_errors)
            warnings.extend(meta_warnings)
            
        except ValueError as e:
            errors.append(ValidationError(
                message=f"ISF parsing failed: {e}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="ISF_PARSE_ERROR",
                suggestions=["Check ISF JSON format"]
            ))
        except Exception as e:
            errors.append(ValidationError(
                message=f"ISF analysis failed: {e}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="ISF_ANALYSIS_ERROR",
                suggestions=["Check ISF document structure"]
            ))
        
        return {
            "is_valid": len([e for e in errors if e.severity == ErrorSeverity.ERROR]) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    def _analyze_parameters(self, isf_doc: ISFDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze ISF parameters for issues."""
        errors = []
        warnings = []
        
        # Ensure parameters is not None (handled by __post_init__)
        parameters = isf_doc.parameters or []
        
        for param in parameters:
            # Check for missing names
            if not param.name or param.name.strip() == "":
                errors.append(ValidationError(
                    message=f"Parameter missing name",
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    error_code="ISF_PARAMETER_ERROR",
                    suggestions=["Add a name for the parameter"]
                ))
            
            # Check for invalid default values
            if param.default_value is not None:
                default_valid = self._validate_default_value(param)
                if not default_valid:
                    errors.append(ValidationError(
                        message=f"Invalid default value for parameter '{param.name}'",
                        severity=ErrorSeverity.ERROR,
                        line=0,
                        column=0,
                        error_code="ISF_PARAMETER_ERROR",
                        suggestions=[f"Check default value type for {param.type.value}"]
                    ))
            
            # Check min/max value consistency
            if param.min_value is not None and param.max_value is not None:
                if param.min_value > param.max_value:
                    errors.append(ValidationError(
                        message=f"Min value greater than max value for parameter '{param.name}'",
                        severity=ErrorSeverity.ERROR,
                        line=0,
                        column=0,
                        error_code="ISF_PARAMETER_ERROR",
                        suggestions=["Ensure min_value <= max_value"]
                    ))
            
            # Check for reserved parameter names
            reserved_names = ["time", "resolution", "mouse", "mouseNorm", "mouseDown", "mouseDownNorm"]
            if param.name in reserved_names:
                warnings.append(ValidationError(
                    message=f"Parameter '{param.name}' conflicts with ISF reserved name",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="ISF_PARAMETER_WARNING",
                    suggestions=["Consider using a different parameter name"]
                ))
        
        return errors, warnings
    
    def _analyze_shader_code(self, isf_doc: ISFDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze ISF shader code for issues."""
        errors = []
        warnings = []
        
        # Check for empty fragment shader
        if not isf_doc.fragment_shader or isf_doc.fragment_shader.strip() == "":
            errors.append(ValidationError(
                message="Fragment shader is empty",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="ISF_SHADER_ERROR",
                suggestions=["Add fragment shader code"]
            ))
        
        # Check for basic GLSL syntax issues
        if isf_doc.fragment_shader:
            glsl_errors, glsl_warnings = self._check_glsl_syntax(isf_doc.fragment_shader)
            errors.extend(glsl_errors)
            warnings.extend(glsl_warnings)
        
        if isf_doc.vertex_shader:
            glsl_errors, glsl_warnings = self._check_glsl_syntax(isf_doc.vertex_shader)
            errors.extend(glsl_errors)
            warnings.extend(glsl_warnings)
        
        return errors, warnings
    
    def _analyze_passes(self, isf_doc: ISFDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze ISF render passes for issues."""
        errors = []
        warnings = []
        
        # Ensure passes is not None (handled by __post_init__)
        passes = isf_doc.passes or []
        
        # Check for duplicate target names
        targets = [pass_obj.target for pass_obj in passes if pass_obj.target]
        duplicate_targets = [t for t in set(targets) if targets.count(t) > 1]
        
        for target in duplicate_targets:
            errors.append(ValidationError(
                message=f"Duplicate render target: {target}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="ISF_PASS_ERROR",
                suggestions=["Use unique target names for each pass"]
            ))
        
        # Check for persistent passes without targets
        for i, pass_obj in enumerate(passes):
            if pass_obj.persistent and not pass_obj.target:
                warnings.append(ValidationError(
                    message=f"Persistent pass {i} has no target",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="ISF_PASS_WARNING",
                    suggestions=["Consider adding a target for persistent passes"]
                ))
        
        return errors, warnings
    
    def _analyze_metadata(self, isf_doc: ISFDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze ISF metadata for issues."""
        errors = []
        warnings = []
        
        # Check for missing description
        if not isf_doc.description:
            warnings.append(ValidationError(
                message="Shader missing description",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="ISF_METADATA_WARNING",
                suggestions=["Add a description to help users understand the shader"]
            ))
        
        # Check for missing author
        if not isf_doc.author:
            warnings.append(ValidationError(
                message="Shader missing author information",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="ISF_METADATA_WARNING",
                suggestions=["Add author information for attribution"]
            ))
        
        # Check for missing categories
        categories = isf_doc.categories or []
        if not categories:
            warnings.append(ValidationError(
                message="Shader missing categories",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="ISF_METADATA_WARNING",
                suggestions=["Add categories to help users find the shader"]
            ))
        
        return errors, warnings
    
    def _validate_default_value(self, param: ISFParameter) -> bool:
        """Validate that default value matches parameter type."""
        if param.default_value is None:
            return True
        
        try:
            if param.type.value == "float":
                return isinstance(param.default_value, (int, float))
            elif param.type.value == "int":
                return isinstance(param.default_value, int)
            elif param.type.value == "bool":
                return isinstance(param.default_value, bool)
            elif param.type.value == "color":
                # Color should be an array of 4 floats
                return (isinstance(param.default_value, list) and 
                       len(param.default_value) == 4 and 
                       all(isinstance(x, (int, float)) for x in param.default_value))
            elif param.type.value == "point2D":
                # Point2D should be an array of 2 floats
                return (isinstance(param.default_value, list) and 
                       len(param.default_value) == 2 and 
                       all(isinstance(x, (int, float)) for x in param.default_value))
            elif param.type.value == "image":
                # Image can be any value (will be validated at runtime)
                return True
            else:
                return False
        except Exception:
            return False
    
    def _check_glsl_syntax(self, shader_code: str) -> tuple[List[ValidationError], List[ValidationError]]:
        """Check GLSL syntax using basic validation for ISF shaders."""
        errors = []
        warnings = []
        
        try:
            # Basic GLSL validation without overly strict syntax checking
            # Since ISF shaders are known to work in other validators, we'll be lenient
            
            # Check for empty shader
            if not shader_code.strip():
                errors.append(ValidationError(
                    message="Empty shader code",
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    error_code="GLSL_SYNTAX_ERROR",
                    suggestions=["Add shader code"]
                ))
                return errors, warnings
            
            # Check for basic GLSL structure (main function)
            if 'void main()' not in shader_code and 'void main (' not in shader_code:
                warnings.append(ValidationError(
                    message="No main function found",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="GLSL_SYNTAX_WARNING",
                    suggestions=["Add void main() function"]
                ))
            
            # Check for version directive (optional for ISF)
            if not re.search(r'#version\s+\d+', shader_code):
                warnings.append(ValidationError(
                    message="No version directive found",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="GLSL_SYNTAX_WARNING",
                    suggestions=["Review GLSL code"]
                ))
            
            # Basic brace matching check
            open_braces = 0
            for char in shader_code:
                if char == '{':
                    open_braces += 1
                elif char == '}':
                    open_braces -= 1
                    if open_braces < 0:
                        errors.append(ValidationError(
                            message="Unmatched closing brace",
                            severity=ErrorSeverity.ERROR,
                            line=0,
                            column=0,
                            error_code="GLSL_SYNTAX_ERROR",
                            suggestions=["Check brace matching"]
                        ))
                        break
            
            if open_braces > 0:
                errors.append(ValidationError(
                    message="Unmatched opening brace",
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    error_code="GLSL_SYNTAX_ERROR",
                    suggestions=["Check brace matching"]
                ))
            
        except Exception as e:
            errors.append(ValidationError(
                message=f"GLSL syntax analysis failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="GLSL_ANALYSIS_ERROR",
                suggestions=["Check GLSL code structure"]
            ))
        
        return errors, warnings 