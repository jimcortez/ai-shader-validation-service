"""
Core error models for validation system
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Severity levels for validation errors."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"


@dataclass
class ValidationError:
    """Base validation error model."""
    message: str
    line: int
    column: int
    severity: ErrorSeverity
    error_code: str
    context: Optional[str] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    @property
    def total_issues(self) -> int:
        """Get total number of issues."""
        return len(self.errors) + len(self.warnings) + len(self.info) 