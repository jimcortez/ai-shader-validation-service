"""
Portability Analyzer for GLSL Shaders

This module analyzes GLSL shaders for portability issues across different
OpenGL versions, hardware platforms, and shader variants.
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from enum import Enum
import re

from ..parser.glsl_ast import (
    GLSLNode, GLSLProgram, GLSLStatement, GLSLExpression,
    GLSLDeclaration, GLSLDeclarator, GLSLIdentifier, GLSLLiteral
)
from ..models.errors import ValidationError, ErrorSeverity


class PortabilityIssueType(Enum):
    """Types of portability issues that can be detected."""
    VERSION_INCOMPATIBILITY = "version_incompatibility"
    HARDWARE_SPECIFIC_FEATURE = "hardware_specific_feature"
    PRECISION_QUALIFIER_MISSING = "precision_qualifier_missing"
    NON_STANDARD_EXTENSION = "non_standard_extension"
    PLATFORM_SPECIFIC_FUNCTION = "platform_specific_function"
    DEPRECATED_FEATURE = "deprecated_feature"


@dataclass
class PortabilityIssue:
    """Represents a portability issue found during analysis."""
    issue_type: PortabilityIssueType
    message: str
    line: int
    column: int
    severity: ErrorSeverity
    context: Optional[str] = None
    suggestions: Optional[List[str]] = None
    affected_platforms: Optional[List[str]] = None


class PortabilityAnalyzer:
    """Analyzes GLSL shaders for portability issues across different platforms."""
    
    def __init__(self):
        self.issues: List[PortabilityIssue] = []
        self.target_version: str = "330"  # Default to GLSL 330
        self.target_platforms: List[str] = ["desktop", "mobile", "web"]
        
        # GLSL version features
        self.version_features = {
            "110": {"builtin_functions": ["texture2D", "gl_FragColor"], "deprecated": []},
            "120": {"builtin_functions": ["texture2D", "gl_FragColor"], "deprecated": []},
            "130": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "140": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "150": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "330": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "400": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "410": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "420": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "430": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "440": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "450": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]},
            "460": {"builtin_functions": ["texture", "fragColor"], "deprecated": ["texture2D", "gl_FragColor"]}
        }
        
        # Platform-specific limitations
        self.platform_limitations = {
            "mobile": {
                "max_texture_size": 4096,
                "max_varying_vectors": 32,
                "max_vertex_uniform_vectors": 256,
                "max_fragment_uniform_vectors": 224,
                "required_precision": True
            },
            "web": {
                "max_texture_size": 4096,
                "max_varying_vectors": 32,
                "max_vertex_uniform_vectors": 256,
                "max_fragment_uniform_vectors": 224,
                "required_precision": True
            },
            "desktop": {
                "max_texture_size": 16384,
                "max_varying_vectors": 32,
                "max_vertex_uniform_vectors": 4096,
                "max_fragment_uniform_vectors": 1024,
                "required_precision": False
            }
        }
        
        # Hardware-specific features
        self.hardware_features = {
            "compute_shaders": ["430", "420", "410", "400"],
            "tessellation": ["400"],
            "geometry_shaders": ["150"],
            "instancing": ["330"],
            "multiple_render_targets": ["300"]
        }
    
    def analyze(self, ast_root: GLSLNode, target_version: str = "330", 
                target_platforms: Optional[List[str]] = None) -> List[PortabilityIssue]:
        """Analyze the AST for portability issues."""
        self.issues.clear()
        self.target_version = target_version
        if target_platforms:
            self.target_platforms = target_platforms
        
        # Perform different types of portability analysis
        self._analyze_version_compatibility(ast_root)
        self._analyze_precision_qualifiers(ast_root)
        self._analyze_platform_limitations(ast_root)
        self._analyze_deprecated_features(ast_root)
        self._analyze_extensions(ast_root)
        
        return self.issues
    
    def _analyze_version_compatibility(self, node: GLSLNode):
        """Analyze GLSL version compatibility."""
        if isinstance(node, GLSLProgram):
            # Check for version-specific features
            for stmt in node.statements:
                self._check_version_specific_features(stmt)
    
    def _check_version_specific_features(self, stmt: GLSLStatement):
        """Check for features that may not be available in target version."""
        if isinstance(stmt, GLSLDeclaration):
            # Check for compute shader features in older versions
            if self.target_version < "430" and self._is_compute_shader_feature(stmt):
                self.issues.append(PortabilityIssue(
                    issue_type=PortabilityIssueType.VERSION_INCOMPATIBILITY,
                    message="Compute shader features require GLSL 430 or higher",
                    line=stmt.line or 0,
                    column=stmt.column or 0,
                    severity=ErrorSeverity.ERROR,
                    suggestions=["Upgrade to GLSL 430+ or remove compute shader features"],
                    affected_platforms=["desktop"]
                ))
    
    def _is_compute_shader_feature(self, stmt: GLSLStatement) -> bool:
        """Check if a statement uses compute shader features."""
        # This would check for compute shader specific features
        # For now, we'll focus on basic checks
        return False
    
    def _analyze_precision_qualifiers(self, node: GLSLNode):
        """Analyze precision qualifier usage for mobile/web platforms."""
        if "mobile" in self.target_platforms or "web" in self.target_platforms:
            if isinstance(node, GLSLProgram):
                has_precision_qualifier = False
                
                # Check for precision qualifier declarations
                for stmt in node.statements:
                    if self._is_precision_declaration(stmt):
                        has_precision_qualifier = True
                        break
                
                if not has_precision_qualifier:
                    self.issues.append(PortabilityIssue(
                        issue_type=PortabilityIssueType.PRECISION_QUALIFIER_MISSING,
                        message="Precision qualifiers are required for mobile/web platforms",
                        line=0,
                        column=0,
                        severity=ErrorSeverity.WARNING,
                        suggestions=["Add precision qualifiers (lowp, mediump, highp) for better compatibility"],
                        affected_platforms=["mobile", "web"]
                    ))
    
    def _is_precision_declaration(self, stmt: GLSLStatement) -> bool:
        """Check if a statement is a precision qualifier declaration."""
        # This would check for precision qualifier declarations
        # For now, we'll focus on basic checks
        return False
    
    def _analyze_platform_limitations(self, node: GLSLNode):
        """Analyze platform-specific limitations."""
        for platform in self.target_platforms:
            if platform in self.platform_limitations:
                limitations = self.platform_limitations[platform]
                self._check_platform_limits(node, platform, limitations)
    
    def _check_platform_limits(self, node: GLSLNode, platform: str, limitations: Dict):
        """Check platform-specific limitations."""
        if isinstance(node, GLSLProgram):
            # Check for uniform count limits
            uniform_count = self._count_uniforms(node)
            max_uniforms = limitations.get("max_fragment_uniform_vectors", 1024)
            
            if uniform_count > max_uniforms:
                self.issues.append(PortabilityIssue(
                    issue_type=PortabilityIssueType.HARDWARE_SPECIFIC_FEATURE,
                    message=f"Too many uniforms ({uniform_count}) for {platform} platform (max: {max_uniforms})",
                    line=0,
                    column=0,
                    severity=ErrorSeverity.WARNING,
                    suggestions=["Reduce uniform count or use texture-based uniforms"],
                    affected_platforms=[platform]
                ))
    
    def _count_uniforms(self, node: GLSLNode) -> int:
        """Count the number of uniform declarations."""
        count = 0
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                if self._is_uniform_declaration(stmt):
                    count += 1
        return count
    
    def _is_uniform_declaration(self, stmt: GLSLStatement) -> bool:
        """Check if a statement is a uniform declaration."""
        # This would check for uniform declarations
        # For now, we'll focus on basic checks
        return False
    
    def _analyze_deprecated_features(self, node: GLSLNode):
        """Analyze usage of deprecated GLSL features."""
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                self._check_deprecated_features(stmt)
    
    def _check_deprecated_features(self, stmt: GLSLStatement):
        """Check for deprecated features in a statement."""
        # Check for deprecated built-in variables
        if self._uses_deprecated_builtins(stmt):
            self.issues.append(PortabilityIssue(
                issue_type=PortabilityIssueType.DEPRECATED_FEATURE,
                message="Usage of deprecated built-in variables",
                line=stmt.line or 0,
                column=stmt.column or 0,
                severity=ErrorSeverity.WARNING,
                suggestions=["Use modern GLSL built-ins instead"],
                affected_platforms=self.target_platforms
            ))
    
    def _uses_deprecated_builtins(self, stmt: GLSLStatement) -> bool:
        """Check if a statement uses deprecated built-in variables."""
        # This would check for deprecated built-ins like gl_FragColor
        # For now, we'll focus on basic checks
        return False
    
    def _analyze_extensions(self, node: GLSLNode):
        """Analyze extension usage for portability."""
        if isinstance(node, GLSLProgram):
            # Check for non-standard extensions
            for stmt in node.statements:
                if self._is_extension_declaration(stmt):
                    extension_name = self._get_extension_name(stmt)
                    if extension_name and not self._is_standard_extension(extension_name):
                        self.issues.append(PortabilityIssue(
                            issue_type=PortabilityIssueType.NON_STANDARD_EXTENSION,
                            message=f"Non-standard extension '{extension_name}' may not be supported on all platforms",
                            line=stmt.line or 0,
                            column=stmt.column or 0,
                            severity=ErrorSeverity.WARNING,
                            suggestions=["Check extension support on target platforms"],
                            affected_platforms=self.target_platforms
                        ))
    
    def _is_extension_declaration(self, stmt: GLSLStatement) -> bool:
        """Check if a statement is an extension declaration."""
        # This would check for extension declarations
        # For now, we'll focus on basic checks
        return False
    
    def _get_extension_name(self, stmt: GLSLStatement) -> Optional[str]:
        """Get the extension name from a declaration."""
        # This would extract extension names
        # For now, we'll focus on basic checks
        return None
    
    def _is_standard_extension(self, extension_name: str) -> bool:
        """Check if an extension is standard and widely supported."""
        standard_extensions = [
            "GL_ARB_texture_rectangle",
            "GL_ARB_shading_language_420pack",
            "GL_ARB_explicit_attrib_location"
        ]
        return extension_name in standard_extensions


class CrossPlatformValidator:
    """Validates shader compatibility across different platforms."""
    
    def __init__(self):
        self.issues: List[PortabilityIssue] = []
    
    def validate(self, ast_root: GLSLNode, platforms: List[str]) -> List[PortabilityIssue]:
        """Validate shader compatibility across specified platforms."""
        self.issues.clear()
        
        # Check compatibility for each platform
        for platform in platforms:
            self._validate_platform_compatibility(ast_root, platform)
        
        return self.issues
    
    def _validate_platform_compatibility(self, node: GLSLNode, platform: str):
        """Validate compatibility for a specific platform."""
        # Platform-specific validation logic
        if platform == "mobile":
            self._validate_mobile_compatibility(node)
        elif platform == "web":
            self._validate_web_compatibility(node)
        elif platform == "desktop":
            self._validate_desktop_compatibility(node)
    
    def _validate_mobile_compatibility(self, node: GLSLNode):
        """Validate mobile platform compatibility."""
        # Check for mobile-specific limitations
        pass
    
    def _validate_web_compatibility(self, node: GLSLNode):
        """Validate web platform compatibility."""
        # Check for web-specific limitations
        pass
    
    def _validate_desktop_compatibility(self, node: GLSLNode):
        """Validate desktop platform compatibility."""
        # Check for desktop-specific limitations
        pass 