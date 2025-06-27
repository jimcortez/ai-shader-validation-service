"""
Validation utility functions
"""
from typing import List, Dict, Any

def aggregate_errors(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Aggregate errors, warnings, and info from multiple validation/analyzer results."""
    errors = []
    warnings = []
    info = []
    for result in results:
        errors.extend(result.get("errors", []))
        warnings.extend(result.get("warnings", []))
        info.extend(result.get("info", []))
    return {
        "errors": errors,
        "warnings": warnings,
        "info": info
    } 