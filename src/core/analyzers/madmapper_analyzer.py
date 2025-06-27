"""
MadMapper Shader Analyzer
"""

import logging
import re
from typing import Dict, Any, List, Optional
from ..parsers.madmapper_parser import MadMapperParser, MadMapperDocument, MadMapperParameter
from ..models.errors import ValidationError, ErrorSeverity

logger = logging.getLogger(__name__)


class MadMapperAnalyzer:
    """Analyzer for MadMapper shaders."""
    
    def __init__(self):
        self.parser = MadMapperParser()
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, madmapper_code: str) -> Dict[str, Any]:
        """
        Analyze MadMapper shader and return validation results.
        
        Args:
            madmapper_code: MadMapper shader code string
            
        Returns:
            Dictionary with analysis results
        """
        errors = []
        warnings = []
        metadata = {}
        
        try:
            # Parse MadMapper document
            madmapper_doc = self.parser.parse(madmapper_code)
            metadata["parsed_document"] = madmapper_doc
            
            # Validate structure
            structure_errors = self.parser.validate_structure(madmapper_code)
            for error in structure_errors:
                errors.append(ValidationError(
                    message=error,
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_STRUCTURE_ERROR",
                    suggestions=["Check MadMapper shader format specification"]
                ))
            
            # Analyze parameters
            param_errors, param_warnings = self._analyze_parameters(madmapper_doc)
            errors.extend(param_errors)
            warnings.extend(param_warnings)
            
            # Analyze shader code
            shader_errors, shader_warnings = self._analyze_shader_code(madmapper_doc)
            errors.extend(shader_errors)
            warnings.extend(shader_warnings)
            
            # Analyze inputs and outputs
            io_errors, io_warnings = self._analyze_inputs_outputs(madmapper_doc)
            errors.extend(io_errors)
            warnings.extend(io_warnings)
            
            # Analyze metadata
            meta_errors, meta_warnings = self._analyze_metadata(madmapper_doc)
            errors.extend(meta_errors)
            warnings.extend(meta_warnings)
            
        except ValueError as e:
            errors.append(ValidationError(
                message=f"MadMapper parsing failed: {e}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="MADMAPPER_PARSE_ERROR",
                suggestions=["Check MadMapper shader format"]
            ))
        except Exception as e:
            errors.append(ValidationError(
                message=f"MadMapper analysis failed: {e}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="MADMAPPER_ANALYSIS_ERROR",
                suggestions=["Check MadMapper document structure"]
            ))
        
        return {
            "is_valid": len([e for e in errors if e.severity == ErrorSeverity.ERROR]) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": metadata
        }
    
    def _analyze_parameters(self, madmapper_doc: MadMapperDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze MadMapper parameters for issues."""
        errors = []
        warnings = []
        
        # Ensure parameters is not None (handled by __post_init__)
        parameters = madmapper_doc.parameters or []
        
        for param in parameters:
            # Check for missing names
            if not param.name or param.name.strip() == "":
                errors.append(ValidationError(
                    message=f"Parameter missing name",
                    severity=ErrorSeverity.ERROR,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_PARAMETER_ERROR",
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
                        error_code="MADMAPPER_PARAMETER_ERROR",
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
                        error_code="MADMAPPER_PARAMETER_ERROR",
                        suggestions=["Ensure min_value <= max_value"]
                    ))
            
            # Check for reserved parameter names
            reserved_names = ["time", "resolution", "mouse", "mouseNorm", "mouseDown", "mouseDownNorm", "projectionMatrix", "modelViewMatrix"]
            if param.name in reserved_names:
                warnings.append(ValidationError(
                    message=f"Parameter '{param.name}' conflicts with MadMapper reserved name",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_PARAMETER_WARNING",
                    suggestions=["Consider using a different parameter name"]
                ))
            
            # Check for enum parameters without values
            if param.type.value == "enum" and not param.values:
                warnings.append(ValidationError(
                    message=f"Enum parameter '{param.name}' has no defined values",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_PARAMETER_WARNING",
                    suggestions=["Define enum values in parameter description"]
                ))
        
        return errors, warnings
    
    def _analyze_shader_code(self, madmapper_doc: MadMapperDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze MadMapper shader code for issues."""
        errors = []
        warnings = []
        
        # Check for empty fragment shader
        if not madmapper_doc.fragment_shader or madmapper_doc.fragment_shader.strip() == "":
            errors.append(ValidationError(
                message="Fragment shader is empty",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="MADMAPPER_SHADER_ERROR",
                suggestions=["Add fragment shader code"]
            ))
        
        # Check for basic GLSL syntax issues in all shader sections
        shader_sections = [
            ("fragment_shader", madmapper_doc.fragment_shader),
            ("vertex_shader", madmapper_doc.vertex_shader),
            ("geometry_shader", madmapper_doc.geometry_shader),
            ("compute_shader", madmapper_doc.compute_shader)
        ]
        
        for section_name, section_code in shader_sections:
            if section_code:
                glsl_errors, glsl_warnings = self._check_glsl_syntax(section_code, section_name)
                errors.extend(glsl_errors)
                warnings.extend(glsl_warnings)
        
        # Check for MadMapper-specific shader requirements
        if madmapper_doc.fragment_shader:
            madmapper_errors, madmapper_warnings = self._check_madmapper_specific_requirements(madmapper_doc.fragment_shader)
            errors.extend(madmapper_errors)
            warnings.extend(madmapper_warnings)
        
        return errors, warnings
    
    def _analyze_inputs_outputs(self, madmapper_doc: MadMapperDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze MadMapper inputs and outputs for issues."""
        errors = []
        warnings = []
        
        # Ensure inputs and outputs are not None (handled by __post_init__)
        inputs = madmapper_doc.inputs or []
        outputs = madmapper_doc.outputs or []
        
        # Check for duplicate input names
        input_names = [input_obj.name for input_obj in inputs]
        duplicate_inputs = [name for name in set(input_names) if input_names.count(name) > 1]
        
        for name in duplicate_inputs:
            errors.append(ValidationError(
                message=f"Duplicate input name: {name}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="MADMAPPER_IO_ERROR",
                suggestions=["Use unique names for inputs"]
            ))
        
        # Check for duplicate output names
        output_names = [output_obj.name for output_obj in outputs]
        duplicate_outputs = [name for name in set(output_names) if output_names.count(name) > 1]
        
        for name in duplicate_outputs:
            errors.append(ValidationError(
                message=f"Duplicate output name: {name}",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="MADMAPPER_IO_ERROR",
                suggestions=["Use unique names for outputs"]
            ))
        
        # Check for valid input/output types
        valid_types = ["float", "vec2", "vec3", "vec4", "int", "bool", "sampler2D", "samplerCube"]
        
        for input_obj in inputs:
            if input_obj.type not in valid_types:
                warnings.append(ValidationError(
                    message=f"Input '{input_obj.name}' has potentially invalid type: {input_obj.type}",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_IO_WARNING",
                    suggestions=[f"Consider using one of: {', '.join(valid_types)}"]
                ))
        
        for output_obj in outputs:
            if output_obj.type not in valid_types:
                warnings.append(ValidationError(
                    message=f"Output '{output_obj.name}' has potentially invalid type: {output_obj.type}",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_IO_WARNING",
                    suggestions=[f"Consider using one of: {', '.join(valid_types)}"]
                ))
        
        return errors, warnings
    
    def _analyze_metadata(self, madmapper_doc: MadMapperDocument) -> tuple[List[ValidationError], List[ValidationError]]:
        """Analyze MadMapper metadata for issues."""
        errors = []
        warnings = []
        
        # Check for missing description
        if not madmapper_doc.description:
            warnings.append(ValidationError(
                message="Shader missing description",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="MADMAPPER_METADATA_WARNING",
                suggestions=["Add a description to help users understand the shader"]
            ))
        
        # Check for missing author
        if not madmapper_doc.author:
            warnings.append(ValidationError(
                message="Shader missing author information",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="MADMAPPER_METADATA_WARNING",
                suggestions=["Add author information for attribution"]
            ))
        
        # Check for missing category
        if not madmapper_doc.category:
            warnings.append(ValidationError(
                message="Shader missing category",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="MADMAPPER_METADATA_WARNING",
                suggestions=["Add a category to help users find the shader"]
            ))
        
        # Check for missing version
        if not madmapper_doc.version:
            warnings.append(ValidationError(
                message="Shader missing version information",
                severity=ErrorSeverity.WARNING,
                line=0,
                column=0,
                error_code="MADMAPPER_METADATA_WARNING",
                suggestions=["Add version information for tracking changes"]
            ))
        
        return errors, warnings
    
    def _validate_default_value(self, param: MadMapperParameter) -> bool:
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
                # Color should be an array of 4 floats or a color name
                if isinstance(param.default_value, list):
                    return len(param.default_value) == 4 and all(isinstance(x, (int, float)) for x in param.default_value)
                else:
                    return isinstance(param.default_value, str)
            elif param.type.value in ["vec2", "vec3", "vec4"]:
                # Vector should be an array of floats
                if isinstance(param.default_value, list):
                    expected_length = int(param.type.value[3])
                    return len(param.default_value) == expected_length and all(isinstance(x, (int, float)) for x in param.default_value)
                else:
                    return False
            elif param.type.value == "texture":
                # Texture can be any value (will be validated at runtime)
                return True
            elif param.type.value == "enum":
                # Enum should be one of the defined values
                if param.values and param.default_value not in param.values:
                    return False
                return True
            else:
                return False
        except Exception:
            return False
    
    def _check_glsl_syntax(self, shader_code: str, section_name: str) -> tuple[List[ValidationError], List[ValidationError]]:
        """Basic GLSL syntax checking."""
        errors = []
        warnings = []
        
        lines = shader_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for unmatched braces
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            if open_braces != close_braces:
                warnings.append(ValidationError(
                    message=f"Potential brace mismatch on line {i} in {section_name}",
                    severity=ErrorSeverity.WARNING,
                    line=i,
                    column=0,
                    error_code="GLSL_SYNTAX_WARNING",
                    suggestions=["Check for unmatched braces"]
                ))
            
            # Check for common GLSL keywords
            if 'main()' in line and 'void' not in line:
                warnings.append(ValidationError(
                    message=f"Main function should be declared as 'void main()' on line {i} in {section_name}",
                    severity=ErrorSeverity.WARNING,
                    line=i,
                    column=0,
                    error_code="GLSL_SYNTAX_WARNING",
                    suggestions=["Use 'void main()' declaration"]
                ))
        
        return errors, warnings
    
    def _check_madmapper_specific_requirements(self, fragment_shader: str) -> tuple[List[ValidationError], List[ValidationError]]:
        """Check MadMapper-specific shader requirements."""
        errors = []
        warnings = []
        
        # Check for gl_FragColor assignment (required for fragment shaders)
        if not re.search(r'gl_FragColor\s*=', fragment_shader):
            errors.append(ValidationError(
                message="Fragment shader must assign to gl_FragColor",
                severity=ErrorSeverity.ERROR,
                line=0,
                column=0,
                error_code="MADMAPPER_SHADER_ERROR",
                suggestions=["Add gl_FragColor assignment in fragment shader"]
            ))
        
        # Check for common MadMapper uniforms
        madmapper_uniforms = ["projectionMatrix", "modelViewMatrix", "resolution", "time"]
        for uniform in madmapper_uniforms:
            if uniform in fragment_shader and not re.search(rf'uniform\s+\w+\s+{uniform}', fragment_shader):
                warnings.append(ValidationError(
                    message=f"MadMapper uniform '{uniform}' used but not declared",
                    severity=ErrorSeverity.WARNING,
                    line=0,
                    column=0,
                    error_code="MADMAPPER_SHADER_WARNING",
                    suggestions=[f"Declare uniform for '{uniform}' if needed"]
                ))
        
        return errors, warnings 