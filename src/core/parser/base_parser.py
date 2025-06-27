"""
Base parser interface for shader formats
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseShaderParser(ABC):
    """Abstract base class for shader parsers"""

    def __init__(self, code: str, parameters: Optional[Dict[str, Any]] = None):
        self.code = code
        self.parameters = parameters or {}

    @abstractmethod
    def parse(self) -> Any:
        """Parse the shader code and return an AST or intermediate representation."""
        pass

    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """Perform syntax and semantic validation. Returns a dict with errors, warnings, etc."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the shader (e.g., uniforms, version, etc.)."""
        pass 