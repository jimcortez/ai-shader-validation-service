"""
ISF (Interactive Shader Format) Parser
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ISFParameterType(Enum):
    """ISF parameter types."""
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    COLOR = "color"
    POINT2D = "point2D"
    IMAGE = "image"


@dataclass
class ISFParameter:
    """Represents an ISF parameter."""
    name: str
    type: ISFParameterType
    default_value: Any
    min_value: Optional[Union[float, int]] = None
    max_value: Optional[Union[float, int]] = None
    values: Optional[List[Any]] = None
    label: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ISFInput:
    """Represents an ISF input."""
    name: str
    type: str
    description: Optional[str] = None


@dataclass
class ISFPass:
    """Represents an ISF render pass."""
    target: Optional[str] = None
    persistent: bool = False
    float: bool = False


@dataclass
class ISFDocument:
    """Represents a parsed ISF document."""
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    categories: Optional[List[str]] = None
    inputs: Optional[List[ISFInput]] = None
    parameters: Optional[List[ISFParameter]] = None
    passes: Optional[List[ISFPass]] = None
    fragment_shader: str = ""
    vertex_shader: Optional[str] = None
    license: Optional[str] = None
    credits: Optional[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.inputs is None:
            self.inputs = []
        if self.parameters is None:
            self.parameters = []
        if self.passes is None:
            self.passes = []


class ISFParser:
    """Parser for ISF (Interactive Shader Format) documents."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, isf_json: str) -> ISFDocument:
        """
        Parse ISF JSON and return an ISFDocument.
        
        Args:
            isf_json: ISF JSON string
            
        Returns:
            Parsed ISFDocument
            
        Raises:
            ValueError: If ISF JSON is invalid
        """
        try:
            data = json.loads(isf_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid ISF JSON: {e}")
        
        # Extract basic metadata
        name = data.get("NAME", "Unnamed Shader")
        description = data.get("DESCRIPTION")
        author = data.get("AUTHOR")
        version = data.get("VERSION")
        categories = data.get("CATEGORIES", [])
        license = data.get("LICENSE")
        credits = data.get("CREDITS")
        
        # Parse inputs
        inputs = self._parse_inputs(data.get("INPUTS", []))
        
        # Parse parameters
        parameters = self._parse_parameters(data.get("INPUTS", []))
        
        # Parse passes
        passes = self._parse_passes(data.get("PASSES", []))
        
        # Extract shader code
        fragment_shader = data.get("FRAGMENT_SHADER", "")
        vertex_shader = data.get("VERTEX_SHADER")
        
        return ISFDocument(
            name=name,
            description=description,
            author=author,
            version=version,
            categories=categories,
            inputs=inputs,
            parameters=parameters,
            passes=passes,
            fragment_shader=fragment_shader,
            vertex_shader=vertex_shader,
            license=license,
            credits=credits
        )
    
    def _parse_inputs(self, inputs_data: List[Dict[str, Any]]) -> List[ISFInput]:
        """Parse ISF inputs."""
        inputs = []
        for input_data in inputs_data:
            name = input_data.get("NAME", "")
            input_type = input_data.get("TYPE", "")
            description = input_data.get("DESCRIPTION")
            
            inputs.append(ISFInput(
                name=name,
                type=input_type,
                description=description
            ))
        
        return inputs
    
    def _parse_parameters(self, inputs_data: List[Dict[str, Any]]) -> List[ISFParameter]:
        """Parse ISF parameters from inputs."""
        parameters = []
        
        for input_data in inputs_data:
            name = input_data.get("NAME", "")
            input_type = input_data.get("TYPE", "")
            default_value = input_data.get("DEFAULT")
            label = input_data.get("LABEL")
            description = input_data.get("DESCRIPTION")
            
            # Convert ISF type to our enum
            try:
                param_type = self._convert_isf_type(input_type)
            except ValueError:
                self.logger.warning(f"Unknown ISF parameter type: {input_type}")
                continue
            
            # Extract min/max values
            min_value = input_data.get("MIN")
            max_value = input_data.get("MAX")
            
            # Extract values for enum-like parameters
            values = input_data.get("VALUES")
            
            parameters.append(ISFParameter(
                name=name,
                type=param_type,
                default_value=default_value,
                min_value=min_value,
                max_value=max_value,
                values=values,
                label=label,
                description=description
            ))
        
        return parameters
    
    def _parse_passes(self, passes_data: List[Dict[str, Any]]) -> List[ISFPass]:
        """Parse ISF render passes."""
        passes = []
        
        for pass_data in passes_data:
            target = pass_data.get("TARGET")
            persistent = pass_data.get("PERSISTENT", False)
            float_pass = pass_data.get("FLOAT", False)
            
            passes.append(ISFPass(
                target=target,
                persistent=persistent,
                float=float_pass
            ))
        
        return passes
    
    def _convert_isf_type(self, isf_type: str) -> ISFParameterType:
        """Convert ISF type string to ISFParameterType enum."""
        type_mapping = {
            "float": ISFParameterType.FLOAT,
            "int": ISFParameterType.INT,
            "bool": ISFParameterType.BOOL,
            "color": ISFParameterType.COLOR,
            "point2D": ISFParameterType.POINT2D,
            "image": ISFParameterType.IMAGE,
        }
        
        if isf_type not in type_mapping:
            raise ValueError(f"Unknown ISF parameter type: {isf_type}")
        
        return type_mapping[isf_type]
    
    def validate_structure(self, isf_json: str) -> List[str]:
        """
        Validate ISF JSON structure and return list of errors.
        
        Args:
            isf_json: ISF JSON string
            
        Returns:
            List of validation errors
        """
        errors = []
        
        try:
            data = json.loads(isf_json)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
            return errors
        
        # Check required fields
        if "NAME" not in data:
            errors.append("Missing required field: NAME")
        
        if "FRAGMENT_SHADER" not in data:
            errors.append("Missing required field: FRAGMENT_SHADER")
        
        # Validate inputs
        inputs = data.get("INPUTS", [])
        for i, input_data in enumerate(inputs):
            if not isinstance(input_data, dict):
                errors.append(f"Input {i} must be an object")
                continue
            
            if "NAME" not in input_data:
                errors.append(f"Input {i} missing required field: NAME")
            
            if "TYPE" not in input_data:
                errors.append(f"Input {i} missing required field: TYPE")
        
        # Validate passes
        passes = data.get("PASSES", [])
        for i, pass_data in enumerate(passes):
            if not isinstance(pass_data, dict):
                errors.append(f"Pass {i} must be an object")
        
        return errors 