"""
MadMapper Shader Parser
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MadMapperParameterType(Enum):
    """MadMapper parameter types."""
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    COLOR = "color"
    VEC2 = "vec2"
    VEC3 = "vec3"
    VEC4 = "vec4"
    TEXTURE = "texture"
    ENUM = "enum"


@dataclass
class MadMapperParameter:
    """Represents a MadMapper parameter."""
    name: str
    type: MadMapperParameterType
    default_value: Any
    min_value: Optional[Union[float, int]] = None
    max_value: Optional[Union[float, int]] = None
    values: Optional[List[Any]] = None
    label: Optional[str] = None
    description: Optional[str] = None
    group: Optional[str] = None


@dataclass
class MadMapperInput:
    """Represents a MadMapper input."""
    name: str
    type: str
    description: Optional[str] = None


@dataclass
class MadMapperOutput:
    """Represents a MadMapper output."""
    name: str
    type: str
    description: Optional[str] = None


@dataclass
class MadMapperDocument:
    """Represents a parsed MadMapper shader document."""
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    inputs: Optional[List[MadMapperInput]] = None
    outputs: Optional[List[MadMapperOutput]] = None
    parameters: Optional[List[MadMapperParameter]] = None
    vertex_shader: str = ""
    fragment_shader: str = ""
    geometry_shader: Optional[str] = None
    compute_shader: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []
        if self.parameters is None:
            self.parameters = []
        if self.metadata is None:
            self.metadata = {}


class MadMapperParser:
    """Parser for MadMapper shader format."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, madmapper_code: str) -> MadMapperDocument:
        """
        Parse MadMapper shader code and return a MadMapperDocument.
        
        Args:
            madmapper_code: MadMapper shader code string
            
        Returns:
            Parsed MadMapperDocument
            
        Raises:
            ValueError: If MadMapper code is invalid
        """
        try:
            # Extract metadata from comments
            metadata = self._extract_metadata(madmapper_code)
            
            # Extract shader code sections
            vertex_shader = self._extract_shader_section(madmapper_code, "VERTEX_SHADER")
            fragment_shader = self._extract_shader_section(madmapper_code, "FRAGMENT_SHADER")
            geometry_shader = self._extract_shader_section(madmapper_code, "GEOMETRY_SHADER")
            compute_shader = self._extract_shader_section(madmapper_code, "COMPUTE_SHADER")
            
            # Parse parameters from comments and code
            parameters = self._parse_parameters(madmapper_code)
            
            # Parse inputs and outputs
            inputs = self._parse_inputs(madmapper_code)
            outputs = self._parse_outputs(madmapper_code)
            
            return MadMapperDocument(
                name=metadata.get("name", "Unnamed MadMapper Shader"),
                description=metadata.get("description"),
                author=metadata.get("author"),
                version=metadata.get("version"),
                category=metadata.get("category"),
                inputs=inputs,
                outputs=outputs,
                parameters=parameters,
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader,
                geometry_shader=geometry_shader,
                compute_shader=compute_shader,
                metadata=metadata
            )
            
        except Exception as e:
            raise ValueError(f"Failed to parse MadMapper shader: {e}")
    
    def _extract_metadata(self, code: str) -> Dict[str, Any]:
        """Extract metadata from MadMapper shader comments."""
        metadata = {}
        
        # Look for metadata in comments
        comment_patterns = [
            r'//\s*@name\s+(.+)',
            r'//\s*@description\s+(.+)',
            r'//\s*@author\s+(.+)',
            r'//\s*@version\s+(.+)',
            r'//\s*@category\s+(.+)',
        ]
        
        for pattern in comment_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE | re.MULTILINE)
            if matches:
                key = pattern.split('@')[1].split()[0].lower()
                metadata[key] = matches[0].strip()
        
        return metadata
    
    def _extract_shader_section(self, code: str, section_name: str) -> str:
        """Extract a specific shader section from the code."""
        # Look for section markers
        section_pattern = rf'//\s*{section_name}\s*\n(.*?)(?=//\s*\w+_SHADER|$)'
        match = re.search(section_pattern, code, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        return ""
    
    def _parse_parameters(self, code: str) -> List[MadMapperParameter]:
        """Parse parameters from MadMapper shader code."""
        parameters = []
        
        # Look for parameter declarations in comments
        param_pattern = r'//\s*@param\s+(\w+)\s+(\w+)(?:\s+(.+))?'
        matches = re.findall(param_pattern, code, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            param_name = match[0]
            param_type_str = match[1].lower()
            param_desc = match[2] if len(match) > 2 else ""
            
            # Parse parameter description for additional info
            param_info = self._parse_parameter_info(param_desc)
            
            # Convert type string to enum
            try:
                param_type = self._convert_madmapper_type(param_type_str)
            except ValueError:
                self.logger.warning(f"Unknown MadMapper parameter type: {param_type_str}")
                continue
            
            # Extract default value from code if available
            default_value = self._extract_default_value(code, param_name, param_type)
            
            parameters.append(MadMapperParameter(
                name=param_name,
                type=param_type,
                default_value=default_value,
                min_value=param_info.get("min"),
                max_value=param_info.get("max"),
                values=param_info.get("values"),
                label=param_info.get("label"),
                description=param_info.get("description"),
                group=param_info.get("group")
            ))
        
        return parameters
    
    def _parse_parameter_info(self, param_desc: str) -> Dict[str, Any]:
        """Parse additional parameter information from description."""
        info = {}
        
        if not param_desc:
            return info
        
        # Extract label
        label_match = re.search(r'label:\s*"([^"]+)"', param_desc)
        if label_match:
            info["label"] = label_match.group(1)
        
        # Extract description
        desc_match = re.search(r'desc:\s*"([^"]+)"', param_desc)
        if desc_match:
            info["description"] = desc_match.group(1)
        
        # Extract min/max values
        min_match = re.search(r'min:\s*([\d.-]+)', param_desc)
        if min_match:
            info["min"] = float(min_match.group(1))
        
        max_match = re.search(r'max:\s*([\d.-]+)', param_desc)
        if max_match:
            info["max"] = float(max_match.group(1))
        
        # Extract values for enum types
        values_match = re.search(r'values:\s*\[([^\]]+)\]', param_desc)
        if values_match:
            values_str = values_match.group(1)
            info["values"] = [v.strip().strip('"\'') for v in values_str.split(',')]
        
        # Extract group
        group_match = re.search(r'group:\s*"([^"]+)"', param_desc)
        if group_match:
            info["group"] = group_match.group(1)
        
        return info
    
    def _extract_default_value(self, code: str, param_name: str, param_type: MadMapperParameterType) -> Any:
        """Extract default value for parameter from shader code."""
        # Look for uniform declarations with default values
        uniform_pattern = rf'uniform\s+{param_type.value}\s+{param_name}\s*=\s*([^;]+);'
        match = re.search(uniform_pattern, code, re.IGNORECASE)
        
        if match:
            value_str = match.group(1).strip()
            return self._parse_value(value_str, param_type)
        
        # Return type-appropriate default
        return self._get_default_value(param_type)
    
    def _parse_value(self, value_str: str, param_type: MadMapperParameterType) -> Any:
        """Parse a value string based on parameter type."""
        try:
            if param_type == MadMapperParameterType.FLOAT:
                return float(value_str)
            elif param_type == MadMapperParameterType.INT:
                return int(value_str)
            elif param_type == MadMapperParameterType.BOOL:
                return value_str.lower() in ('true', '1', 'yes')
            elif param_type in [MadMapperParameterType.VEC2, MadMapperParameterType.VEC3, MadMapperParameterType.VEC4]:
                # Parse vector values like vec3(1.0, 0.0, 0.0)
                vec_match = re.search(r'\(([^)]+)\)', value_str)
                if vec_match:
                    values = [float(v.strip()) for v in vec_match.group(1).split(',')]
                    return values
            elif param_type == MadMapperParameterType.COLOR:
                # Parse color values
                if value_str.startswith('vec'):
                    return self._parse_value(value_str, MadMapperParameterType.VEC4)
                else:
                    # Assume it's a color name or hex
                    return value_str
            else:
                return value_str
        except Exception:
            return self._get_default_value(param_type)
    
    def _get_default_value(self, param_type: MadMapperParameterType) -> Any:
        """Get default value for parameter type."""
        defaults = {
            MadMapperParameterType.FLOAT: 0.0,
            MadMapperParameterType.INT: 0,
            MadMapperParameterType.BOOL: False,
            MadMapperParameterType.COLOR: [1.0, 1.0, 1.0, 1.0],
            MadMapperParameterType.VEC2: [0.0, 0.0],
            MadMapperParameterType.VEC3: [0.0, 0.0, 0.0],
            MadMapperParameterType.VEC4: [0.0, 0.0, 0.0, 1.0],
            MadMapperParameterType.TEXTURE: None,
            MadMapperParameterType.ENUM: None,
        }
        return defaults.get(param_type, None)
    
    def _convert_madmapper_type(self, type_str: str) -> MadMapperParameterType:
        """Convert MadMapper type string to enum."""
        type_mapping = {
            "float": MadMapperParameterType.FLOAT,
            "int": MadMapperParameterType.INT,
            "bool": MadMapperParameterType.BOOL,
            "color": MadMapperParameterType.COLOR,
            "vec2": MadMapperParameterType.VEC2,
            "vec3": MadMapperParameterType.VEC3,
            "vec4": MadMapperParameterType.VEC4,
            "texture": MadMapperParameterType.TEXTURE,
            "enum": MadMapperParameterType.ENUM,
        }
        
        if type_str not in type_mapping:
            raise ValueError(f"Unknown MadMapper parameter type: {type_str}")
        
        return type_mapping[type_str]
    
    def _parse_inputs(self, code: str) -> List[MadMapperInput]:
        """Parse inputs from MadMapper shader code."""
        inputs = []
        
        # Look for input declarations
        input_pattern = r'//\s*@input\s+(\w+)\s+(\w+)(?:\s+(.+))?'
        matches = re.findall(input_pattern, code, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            input_name = match[0]
            input_type = match[1]
            input_desc = match[2] if len(match) > 2 else ""
            
            inputs.append(MadMapperInput(
                name=input_name,
                type=input_type,
                description=input_desc.strip() if input_desc else None
            ))
        
        return inputs
    
    def _parse_outputs(self, code: str) -> List[MadMapperOutput]:
        """Parse outputs from MadMapper shader code."""
        outputs = []
        
        # Look for output declarations
        output_pattern = r'//\s*@output\s+(\w+)\s+(\w+)(?:\s+(.+))?'
        matches = re.findall(output_pattern, code, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            output_name = match[0]
            output_type = match[1]
            output_desc = match[2] if len(match) > 2 else ""
            
            outputs.append(MadMapperOutput(
                name=output_name,
                type=output_type,
                description=output_desc.strip() if output_desc else None
            ))
        
        return outputs
    
    def validate_structure(self, madmapper_code: str) -> List[str]:
        """
        Validate MadMapper shader structure and return list of errors.
        
        Args:
            madmapper_code: MadMapper shader code string
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for required sections
        if not self._extract_shader_section(madmapper_code, "FRAGMENT_SHADER"):
            errors.append("Missing FRAGMENT_SHADER section")
        
        # Check for valid parameter declarations
        param_pattern = r'//\s*@param\s+(\w+)\s+(\w+)'
        param_matches = re.findall(param_pattern, madmapper_code, re.IGNORECASE | re.MULTILINE)
        
        for param_name, param_type in param_matches:
            try:
                self._convert_madmapper_type(param_type.lower())
            except ValueError:
                errors.append(f"Invalid parameter type '{param_type}' for parameter '{param_name}'")
        
        # Check for valid GLSL syntax in shader sections
        shader_sections = ["VERTEX_SHADER", "FRAGMENT_SHADER", "GEOMETRY_SHADER", "COMPUTE_SHADER"]
        for section in shader_sections:
            section_code = self._extract_shader_section(madmapper_code, section)
            if section_code:
                glsl_errors = self._validate_glsl_syntax(section_code)
                for error in glsl_errors:
                    errors.append(f"{section}: {error}")
        
        return errors
    
    def _validate_glsl_syntax(self, shader_code: str) -> List[str]:
        """Basic GLSL syntax validation."""
        errors = []
        
        # Check for basic GLSL structure
        if not re.search(r'void\s+main\s*\(', shader_code):
            errors.append("Missing main function")
        
        # Check for unmatched braces
        brace_count = shader_code.count('{') - shader_code.count('}')
        if brace_count != 0:
            errors.append("Unmatched braces")
        
        # Check for semicolons after statements
        lines = shader_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}'):
                if re.search(r'\b(if|for|while|do)\b', line):
                    continue  # Control structures don't need semicolons
                if re.search(r'\b(uniform|varying|attribute|in|out)\b', line):
                    continue  # Declarations don't need semicolons
                if line.startswith('//') or line.startswith('/*'):
                    continue  # Comments don't need semicolons
                if not re.search(r'[{}]', line):  # Lines with braces don't need semicolons
                    errors.append(f"Missing semicolon on line {i}")
        
        return errors 