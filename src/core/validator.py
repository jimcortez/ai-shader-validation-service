"""
Core validation engine orchestrator
"""
from typing import Dict, Any, Optional, Type
from src.core.parser.base_parser import BaseShaderParser
import logging

logger = logging.getLogger("ai_shader_validator.core.validator")

class ValidationEngine:
    """Orchestrates shader validation using pluggable parsers."""
    
    def __init__(self):
        self.parsers: Dict[str, Type[BaseShaderParser]] = {}

    def register_parser(self, format_name: str, parser_cls: Type[BaseShaderParser]):
        """Register a parser for a shader format."""
        self.parsers[format_name.lower()] = parser_cls
        logger.info(f"Registered parser for format: {format_name}")

    def validate_shader(self, code: str, format_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate a shader using the appropriate parser."""
        parser_cls = self.parsers.get(format_name.lower())
        if not parser_cls:
            logger.error(f"No parser registered for format: {format_name}")
            return {
                "status": "error",
                "errors": [
                    {"message": f"No parser registered for format: {format_name}", "severity": "error"}
                ]
            }
        parser = parser_cls(code, parameters)
        parse_result = parser.parse()
        validation_result = parser.validate()
        metadata = parser.get_metadata()
        return {
            "status": "success" if not validation_result.get("errors") else "error",
            "parse_result": parse_result,
            "validation_result": validation_result,
            "metadata": metadata
        } 