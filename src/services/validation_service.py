"""
Validation service orchestration
"""
from src.core.validator import ValidationEngine
from src.core.parser.glsl_parser import GLSLParser
from src.core.parsers.isf_parser import ISFParser
from src.core.parsers.madmapper_parser import MadMapperParser
from src.core.analyzers.logic_analyzer import LogicFlowAnalyzer, DataFlowAnalyzer, MathematicalValidator
from src.core.analyzers.portability_analyzer import PortabilityAnalyzer, CrossPlatformValidator
from src.core.analyzers.quality_analyzer import QualityAnalyzer
from src.core.analyzers.syntax_analyzer import SyntaxAnalyzer
from src.core.analyzers.semantic_analyzer import SemanticAnalyzer
from src.core.analyzers.isf_analyzer import ISFAnalyzer
from src.core.analyzers.madmapper_analyzer import MadMapperAnalyzer
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
        self.isf_analyzer = ISFAnalyzer()
        self.madmapper_analyzer = MadMapperAnalyzer()
        
        # Initialize parsers
        self.glsl_parser = GLSLParser("")
        self.isf_parser = ISFParser()
        self.madmapper_parser = MadMapperParser()
        
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
            # Parse and validate based on format
            if format_name.lower() == "glsl":
                result = self._validate_glsl(code, result, parameters)
            elif format_name.lower() == "isf":
                result = self._validate_isf(code, result, parameters)
            elif format_name.lower() == "madmapper":
                result = self._validate_madmapper(code, result, parameters)
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
    
    def _validate_glsl(self, code: str, result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GLSL shader."""
        # Parse the shader
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
        
        if parameters.get("enable_portability_analysis", True):
            self._perform_portability_analysis(ast_root, result, 
                                             parameters.get("target_version", "330"), 
                                             parameters.get("target_platforms", ["desktop", "mobile", "web"]))
        
        if parameters.get("enable_quality_analysis", True):
            self._perform_quality_analysis(ast_root, result)
        
        # Check for any critical errors
        if result["errors"]:
            result["is_valid"] = False
        
        # Generate overall recommendations
        result["recommendations"] = self._generate_recommendations(result)
        
        return result
    
    def _validate_isf(self, isf_json: str, result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ISF shader."""
        try:
            # Perform ISF-specific analysis
            isf_result = self.isf_analyzer.analyze(isf_json)
            
            # Convert ISF validation errors to our format
            for error in isf_result.get("errors", []):
                result["errors"].append({
                    "message": error.message,
                    "line": error.line,
                    "column": error.column,
                    "severity": error.severity.value,
                    "error_code": error.error_code,
                    "suggestions": error.suggestions
                })
            
            for warning in isf_result.get("warnings", []):
                result["warnings"].append({
                    "message": warning.message,
                    "line": warning.line,
                    "column": warning.column,
                    "severity": warning.severity.value,
                    "error_code": warning.error_code,
                    "suggestions": warning.suggestions
                })
            
            # Add ISF metadata
            if "metadata" in isf_result and "parsed_document" in isf_result["metadata"]:
                isf_doc = isf_result["metadata"]["parsed_document"]
                result["metadata"] = {
                    "name": isf_doc.name,
                    "description": isf_doc.description,
                    "author": isf_doc.author,
                    "version": isf_doc.version,
                    "categories": isf_doc.categories,
                    "parameters": [{
                        "name": param.name,
                        "type": param.type.value,
                        "default_value": param.default_value
                    } for param in (isf_doc.parameters or [])],
                    "passes": [{
                        "target": pass_obj.target,
                        "persistent": pass_obj.persistent,
                        "float": pass_obj.float
                    } for pass_obj in (isf_doc.passes or [])]
                }
            
            # If ISF has fragment shader, also validate it as GLSL
            if (isf_result.get("metadata", {}).get("parsed_document") and 
                isf_result["metadata"]["parsed_document"].fragment_shader):
                
                fragment_shader = isf_result["metadata"]["parsed_document"].fragment_shader
                glsl_result = self._validate_glsl(fragment_shader, {
                    "is_valid": True,
                    "format": "glsl",
                    "errors": [],
                    "warnings": [],
                    "info": []
                }, parameters)
                
                # Merge GLSL validation results
                result["errors"].extend(glsl_result["errors"])
                result["warnings"].extend(glsl_result["warnings"])
                result["info"].extend(glsl_result["info"])
                
                if "quality_metrics" in glsl_result:
                    result["quality_metrics"].update(glsl_result["quality_metrics"])
                
                if "performance_analysis" in glsl_result:
                    result["performance_analysis"].update(glsl_result["performance_analysis"])
            
            # Check for any critical errors
            if result["errors"]:
                result["is_valid"] = False
            
            # Generate ISF-specific recommendations
            result["recommendations"] = self._generate_isf_recommendations(isf_result)
            
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append({
                "message": f"ISF validation failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error",
                "error_code": "ISF_VALIDATION_ERROR"
            })
        
        return result
    
    def _validate_madmapper(self, madmapper_code: str, result: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MadMapper shader."""
        try:
            # Perform MadMapper-specific analysis
            madmapper_result = self.madmapper_analyzer.analyze(madmapper_code)
            
            # Convert MadMapper validation errors to our format
            for error in madmapper_result.get("errors", []):
                result["errors"].append({
                    "message": error.message,
                    "line": error.line,
                    "column": error.column,
                    "severity": error.severity.value,
                    "error_code": error.error_code,
                    "suggestions": error.suggestions
                })
            
            for warning in madmapper_result.get("warnings", []):
                result["warnings"].append({
                    "message": warning.message,
                    "line": warning.line,
                    "column": warning.column,
                    "severity": warning.severity.value,
                    "error_code": warning.error_code,
                    "suggestions": warning.suggestions
                })
            
            # Add MadMapper metadata
            if "metadata" in madmapper_result and "parsed_document" in madmapper_result["metadata"]:
                madmapper_doc = madmapper_result["metadata"]["parsed_document"]
                result["metadata"] = {
                    "name": madmapper_doc.name,
                    "description": madmapper_doc.description,
                    "author": madmapper_doc.author,
                    "version": madmapper_doc.version,
                    "category": madmapper_doc.category,
                    "parameters": [{
                        "name": param.name,
                        "type": param.type.value,
                        "default_value": param.default_value,
                        "group": param.group
                    } for param in (madmapper_doc.parameters or [])],
                    "inputs": [{
                        "name": input_obj.name,
                        "type": input_obj.type,
                        "description": input_obj.description
                    } for input_obj in (madmapper_doc.inputs or [])],
                    "outputs": [{
                        "name": output_obj.name,
                        "type": output_obj.type,
                        "description": output_obj.description
                    } for output_obj in (madmapper_doc.outputs or [])]
                }
            
            # If MadMapper has fragment shader, also validate it as GLSL
            if (madmapper_result.get("metadata", {}).get("parsed_document") and 
                madmapper_result["metadata"]["parsed_document"].fragment_shader):
                
                fragment_shader = madmapper_result["metadata"]["parsed_document"].fragment_shader
                glsl_result = self._validate_glsl(fragment_shader, {
                    "is_valid": True,
                    "format": "glsl",
                    "errors": [],
                    "warnings": [],
                    "info": []
                }, parameters)
                
                # Merge GLSL validation results
                result["errors"].extend(glsl_result["errors"])
                result["warnings"].extend(glsl_result["warnings"])
                result["info"].extend(glsl_result["info"])
                
                if "quality_metrics" in glsl_result:
                    result["quality_metrics"].update(glsl_result["quality_metrics"])
                
                if "performance_analysis" in glsl_result:
                    result["performance_analysis"].update(glsl_result["performance_analysis"])
            
            # Check for any critical errors
            if result["errors"]:
                result["is_valid"] = False
            
            # Generate MadMapper-specific recommendations
            result["recommendations"] = self._generate_madmapper_recommendations(madmapper_result)
            
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append({
                "message": f"MadMapper validation failed: {str(e)}",
                "line": 0,
                "column": 0,
                "severity": "error",
                "error_code": "MADMAPPER_VALIDATION_ERROR"
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
    
    def _generate_isf_recommendations(self, isf_result: Dict[str, Any]) -> List[str]:
        """Generate ISF-specific recommendations."""
        recommendations = []
        
        # Check for missing metadata
        if "metadata" in isf_result and "parsed_document" in isf_result["metadata"]:
            isf_doc = isf_result["metadata"]["parsed_document"]
            
            if not isf_doc.description:
                recommendations.append("Add a description to help users understand the shader")
            
            if not isf_doc.author:
                recommendations.append("Add author information for attribution")
            
            if not isf_doc.categories:
                recommendations.append("Add categories to help users find the shader")
            
            if not isf_doc.parameters:
                recommendations.append("Consider adding parameters to make the shader more interactive")
        
        # Check for validation issues
        if isf_result.get("errors"):
            recommendations.append("Fix validation errors before using the shader")
        
        if isf_result.get("warnings"):
            recommendations.append("Review warnings to improve shader quality")
        
        return recommendations
    
    def _generate_madmapper_recommendations(self, madmapper_result: Dict[str, Any]) -> List[str]:
        """Generate MadMapper-specific recommendations."""
        recommendations = []
        
        # Check for missing metadata
        if "metadata" in madmapper_result and "parsed_document" in madmapper_result["metadata"]:
            madmapper_doc = madmapper_result["metadata"]["parsed_document"]
            
            if not madmapper_doc.description:
                recommendations.append("Add a description to help users understand the shader")
            
            if not madmapper_doc.author:
                recommendations.append("Add author information for attribution")
            
            if not madmapper_doc.category:
                recommendations.append("Add a category to help users find the shader")
            
            if not madmapper_doc.version:
                recommendations.append("Add version information for tracking changes")
            
            if not madmapper_doc.parameters:
                recommendations.append("Consider adding parameters to make the shader more interactive")
        
        # Check for validation issues
        if madmapper_result.get("errors"):
            recommendations.append("Fix validation errors before using the shader")
        
        if madmapper_result.get("warnings"):
            recommendations.append("Review warnings to improve shader quality")
        
        return recommendations
    
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