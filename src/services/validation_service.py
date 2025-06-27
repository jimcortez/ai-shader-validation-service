"""
Validation service orchestration
"""
from src.core.validator import ValidationEngine
from typing import Dict, Any, Optional

validation_engine = ValidationEngine()

class ValidationService:
    """Service for orchestrating shader validation."""
    def __init__(self):
        self.engine = validation_engine

    def validate(self, code: str, format_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.engine.validate_shader(code, format_name, parameters)

validation_service = ValidationService() 