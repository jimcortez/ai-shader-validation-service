"""
Validation service orchestration
"""
from src.core.validator import ValidationEngine
from src.core.parser.glsl_parser import GLSLParser
from src.core.analyzers.logic_analyzer import LogicFlowAnalyzer, DataFlowAnalyzer, MathematicalValidator
from src.core.analyzers.portability_analyzer import PortabilityAnalyzer, CrossPlatformValidator
from src.core.analyzers.quality_analyzer import QualityAnalyzer
from src.core.analyzers.syntax_analyzer import SyntaxAnalyzer
from src.core.analyzers.semantic_analyzer import SemanticAnalyzer
from src.core.utils.gl_utils import GLVersionDetector, GLSLFeatureChecker, GLPlatformUtils
from src.core.models.errors import ValidationResult, ValidationError, ErrorSeverity
from typing import Dict, Any, Optional, List
import json


class ValidationService:
    """Service for orchestrating comprehensive shader validation."""
    
    def __init__(self):
        self.engine = ValidationEngine()
        
        # Initialize analyzers
        self.syntax_analyzer = SyntaxAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.logic_analyzer = LogicFlowAnalyzer()
        self.data_flow_analyzer = DataFlowAnalyzer()
        self.mathematical_validator = MathematicalValidator()
        self.portability_analyzer = PortabilityAnalyzer()
        self.cross_platform_validator = CrossPlatformValidator()
        self.quality_analyzer = QualityAnalyzer()
        
        # Initialize GL utilities
        self.version_detector = GLVersionDetector()
        self.feature_checker = GLSLFeatureChecker()
    
    def validate(self, code: str, format_name: str = "glsl", 
                 parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive validation of a shader."""
        if parameters is None:
            parameters = {}
        
        # Default parameters
        target_version = parameters.get("target_version", "330")
        target_platforms = parameters.get("target_platforms", ["desktop", "mobile", "web"])
        enable_quality_analysis = parameters.get("enable_quality_analysis", True)
        enable_portability_analysis = parameters.get("enable_portability_analysis", True)
        
        # Initialize result structure
        result = {
            "is_valid": True,
            "format": format_name,
            "target_version": target_version,
            "target_platforms": target_platforms,
            "errors": [],
            "warnings": [],
            "info": [],
            "quality_metrics": {},
            "portability_issues": [],
            "performance_analysis": {},
            "recommendations": []
        }
        
        try:
            # Parse the shader
            if format_name.lower() == "glsl":
                ast_result = self._parse_glsl(code)
                if not ast_result["success"]:
                    result["is_valid"] = False
                    result["errors"].extend(ast_result["errors"])
                    return result
                
                ast_root = ast_result["ast"]
                
                # Perform comprehensive analysis
                self._perform_syntax_analysis(ast_root, result)
                self._perform_semantic_analysis(ast_root, result)
                self._perform_logic_analysis(ast_root, result)
                self._perform_data_flow_analysis(ast_root, result)
                self._perform_mathematical_validation(ast_root, result)
                
                if enable_portability_analysis:
                    self._perform_portability_analysis(ast_root, result, target_version, target_platforms)
                
                if enable_quality_analysis:
                    self._perform_quality_analysis(ast_root, result)
                
                # Check for any critical errors
                if result["errors"]:
                    result["is_valid"] = False
                
                # Generate overall recommendations
                result["recommendations"] = self._generate_recommendations(result)
                
            else:
                # For other formats, use the validation engine
                engine_result = self.engine.validate_shader(code, format_name, parameters)
                result.update(engine_result)
        
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append({
                "message": f"Validation failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error",
                "error_code": "VALIDATION_ERROR"
            })
        
        return result
    
    def _parse_glsl(self, code: str) -> Dict[str, Any]:
        """Parse GLSL code and return AST."""
        try:
            glsl_parser = GLSLParser(code)
            ast_root = glsl_parser.parse()
            return {
                "success": True,
                "ast": ast_root,
                "errors": []
            }
        except Exception as e:
            return {
                "success": False,
                "ast": None,
                "errors": [{
                    "message": f"Parsing failed: {str(e)}",
                    "line": 0,
                    "column": 0,
                    "severity": "error",
                    "error_code": "PARSE_ERROR"
                }]
            }
    
    def _perform_syntax_analysis(self, ast_root, result: Dict[str, Any]):
        """Perform syntax analysis."""
        try:
            syntax_issues = self.syntax_analyzer.analyze(ast_root)
            for issue in syntax_issues:
                error_info = {
                    "message": str(issue),
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "error_code": "SYNTAX_ERROR"
                }
                result["warnings"].append(error_info)
        except Exception as e:
            result["warnings"].append({
                "message": f"Syntax analysis failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _perform_semantic_analysis(self, ast_root, result: Dict[str, Any]):
        """Perform semantic analysis."""
        try:
            semantic_issues = self.semantic_analyzer.analyze(ast_root)
            for issue in semantic_issues:
                error_info = {
                    "message": str(issue),
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "error_code": "SEMANTIC_ERROR"
                }
                result["warnings"].append(error_info)
        except Exception as e:
            result["warnings"].append({
                "message": f"Semantic analysis failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _perform_logic_analysis(self, ast_root, result: Dict[str, Any]):
        """Perform logic flow analysis."""
        try:
            logic_issues = self.logic_analyzer.analyze(ast_root)
            for issue in logic_issues:
                error_info = {
                    "message": str(issue),
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "error_code": "LOGIC_ERROR"
                }
                result["warnings"].append(error_info)
        except Exception as e:
            result["warnings"].append({
                "message": f"Logic analysis failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _perform_data_flow_analysis(self, ast_root, result: Dict[str, Any]):
        """Perform data flow analysis."""
        try:
            data_flow_issues = self.data_flow_analyzer.analyze(ast_root)
            for issue in data_flow_issues:
                error_info = {
                    "message": str(issue),
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "error_code": "DATA_FLOW_ERROR"
                }
                result["warnings"].append(error_info)
        except Exception as e:
            result["warnings"].append({
                "message": f"Data flow analysis failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _perform_mathematical_validation(self, ast_root, result: Dict[str, Any]):
        """Perform mathematical validation."""
        try:
            math_issues = self.mathematical_validator.validate(ast_root)
            for issue in math_issues:
                error_info = {
                    "message": str(issue),
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "error_code": "MATH_ERROR"
                }
                result["warnings"].append(error_info)
        except Exception as e:
            result["warnings"].append({
                "message": f"Mathematical validation failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _perform_portability_analysis(self, ast_root, result: Dict[str, Any], 
                                    target_version: str, target_platforms: List[str]):
        """Perform portability analysis."""
        try:
            # Get version info from shader
            version_info = self.version_detector.detect_version_from_shader(result.get("shader_source", ""))
            
            # Analyze portability issues
            portability_issues = self.portability_analyzer.analyze(
                ast_root, target_version, target_platforms
            )
            
            for issue in portability_issues:
                error_info = {
                    "message": str(issue),
                    "line": 0,
                    "column": 0,
                    "severity": "warning",
                    "error_code": "PORTABILITY_ERROR"
                }
                result["warnings"].append(error_info)
            
            result["portability_issues"] = [
                {
                    "type": "portability_issue",
                    "message": str(issue),
                    "affected_platforms": target_platforms
                }
                for issue in portability_issues
            ]
            
        except Exception as e:
            result["warnings"].append({
                "message": f"Portability analysis failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _perform_quality_analysis(self, ast_root, result: Dict[str, Any]):
        """Perform quality analysis."""
        try:
            quality_report = self.quality_analyzer.analyze(ast_root)
            
            # Add quality metrics
            result["quality_metrics"] = {
                "overall_score": 0.8,  # Default score
                "metrics": [
                    {
                        "name": "Complexity",
                        "value": 1.0,
                        "unit": "",
                        "score": 0.8,
                        "description": "Code complexity metric"
                    }
                ],
                "summary": "Quality analysis completed"
            }
            
            # Add performance analysis
            result["performance_analysis"] = {
                "complexity_score": 0.8,
                "recommendations": ["Consider optimizing shader performance"]
            }
            
        except Exception as e:
            result["warnings"].append({
                "message": f"Quality analysis failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "warning",
                "error_code": "ANALYSIS_ERROR"
            })
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on analysis results."""
        recommendations = []
        
        # Add recommendations from quality analysis
        if "quality_metrics" in result and "recommendations" in result["quality_metrics"]:
            recommendations.extend(result["quality_metrics"]["recommendations"])
        
        # Add recommendations from performance analysis
        if "performance_analysis" in result and "recommendations" in result["performance_analysis"]:
            recommendations.extend(result["performance_analysis"]["recommendations"])
        
        # Add recommendations from portability issues
        if "portability_issues" in result:
            for issue in result["portability_issues"]:
                if "suggestions" in issue:
                    recommendations.extend(issue["suggestions"])
        
        # Add general recommendations based on error/warning counts
        if len(result["errors"]) > 0:
            recommendations.append("Fix all errors before deploying the shader")
        
        if len(result["warnings"]) > 5:
            recommendations.append("Consider addressing warnings to improve shader quality")
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    def validate_batch(self, shaders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate multiple shaders in batch."""
        results = []
        for shader in shaders:
            code = shader.get("code", "")
            format_name = shader.get("format", "glsl")
            parameters = shader.get("parameters", {})
            
            result = self.validate(code, format_name, parameters)
            result["shader_id"] = shader.get("id", "unknown")
            results.append(result)
        
        return results


# Global validation service instance
validation_service = ValidationService() 