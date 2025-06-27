"""
GL Utilities for OpenGL Version Detection and Feature Checking

This module provides utilities for detecting OpenGL versions, checking feature support,
and handling platform-specific OpenGL capabilities.
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import re


class GLVersion(Enum):
    """OpenGL versions."""
    GL_1_0 = "1.0"
    GL_1_1 = "1.1"
    GL_1_2 = "1.2"
    GL_1_3 = "1.3"
    GL_1_4 = "1.4"
    GL_1_5 = "1.5"
    GL_2_0 = "2.0"
    GL_2_1 = "2.1"
    GL_3_0 = "3.0"
    GL_3_1 = "3.1"
    GL_3_2 = "3.2"
    GL_3_3 = "3.3"
    GL_4_0 = "4.0"
    GL_4_1 = "4.1"
    GL_4_2 = "4.2"
    GL_4_3 = "4.3"
    GL_4_4 = "4.4"
    GL_4_5 = "4.5"
    GL_4_6 = "4.6"


class GLSLVersion(Enum):
    """GLSL versions."""
    GLSL_110 = "110"
    GLSL_120 = "120"
    GLSL_130 = "130"
    GLSL_140 = "140"
    GLSL_150 = "150"
    GLSL_330 = "330"
    GLSL_400 = "400"
    GLSL_410 = "410"
    GLSL_420 = "420"
    GLSL_430 = "430"
    GLSL_440 = "440"
    GLSL_450 = "450"
    GLSL_460 = "460"


class GLFeature(Enum):
    """OpenGL features."""
    SHADER_OBJECTS = "shader_objects"
    VERTEX_SHADER = "vertex_shader"
    FRAGMENT_SHADER = "fragment_shader"
    GEOMETRY_SHADER = "geometry_shader"
    TESSELATION_SHADER = "tesselation_shader"
    COMPUTE_SHADER = "compute_shader"
    MULTIPLE_RENDER_TARGETS = "multiple_render_targets"
    TEXTURE_ARRAYS = "texture_arrays"
    TEXTURE_BUFFERS = "texture_buffers"
    CUBE_MAP_ARRAYS = "cube_map_arrays"
    INSTANCED_RENDERING = "instanced_rendering"
    TRANSFORM_FEEDBACK = "transform_feedback"
    UNIFORM_BUFFER_OBJECTS = "uniform_buffer_objects"
    SHADER_STORAGE_BUFFER_OBJECTS = "shader_storage_buffer_objects"
    ATOMIC_COUNTERS = "atomic_counters"
    IMAGE_LOAD_STORE = "image_load_store"


@dataclass
class GLVersionInfo:
    """Information about an OpenGL version."""
    version: GLVersion
    glsl_version: GLSLVersion
    features: Set[GLFeature]
    max_texture_size: int
    max_vertex_uniform_vectors: int
    max_fragment_uniform_vectors: int
    max_varying_vectors: int
    max_vertex_attribs: int
    max_texture_units: int


class GLVersionDetector:
    """Detects OpenGL version and capabilities."""
    
    def __init__(self):
        # Version to feature mapping
        self.version_features = {
            GLVersion.GL_2_0: {
                GLSLVersion.GLSL_110,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER
            },
            GLVersion.GL_2_1: {
                GLSLVersion.GLSL_120,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER
            },
            GLVersion.GL_3_0: {
                GLSLVersion.GLSL_130,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS
            },
            GLVersion.GL_3_1: {
                GLSLVersion.GLSL_140,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS
            },
            GLVersion.GL_3_2: {
                GLSLVersion.GLSL_150,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS
            },
            GLVersion.GL_3_3: {
                GLSLVersion.GLSL_330,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS
            },
            GLVersion.GL_4_0: {
                GLSLVersion.GLSL_400,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS
            },
            GLVersion.GL_4_1: {
                GLSLVersion.GLSL_410,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS
            },
            GLVersion.GL_4_2: {
                GLSLVersion.GLSL_420,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS,
                GLFeature.ATOMIC_COUNTERS
            },
            GLVersion.GL_4_3: {
                GLSLVersion.GLSL_430,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.COMPUTE_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.SHADER_STORAGE_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS,
                GLFeature.ATOMIC_COUNTERS,
                GLFeature.IMAGE_LOAD_STORE
            },
            GLVersion.GL_4_4: {
                GLSLVersion.GLSL_440,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.COMPUTE_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.SHADER_STORAGE_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS,
                GLFeature.ATOMIC_COUNTERS,
                GLFeature.IMAGE_LOAD_STORE
            },
            GLVersion.GL_4_5: {
                GLSLVersion.GLSL_450,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.COMPUTE_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.SHADER_STORAGE_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS,
                GLFeature.ATOMIC_COUNTERS,
                GLFeature.IMAGE_LOAD_STORE
            },
            GLVersion.GL_4_6: {
                GLSLVersion.GLSL_460,
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.COMPUTE_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_BUFFERS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.SHADER_STORAGE_BUFFER_OBJECTS,
                GLFeature.CUBE_MAP_ARRAYS,
                GLFeature.ATOMIC_COUNTERS,
                GLFeature.IMAGE_LOAD_STORE
            }
        }
        
        # Version to limits mapping
        self.version_limits = {
            GLVersion.GL_2_0: {
                "max_texture_size": 1024,
                "max_vertex_uniform_vectors": 128,
                "max_fragment_uniform_vectors": 64,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 2
            },
            GLVersion.GL_3_0: {
                "max_texture_size": 2048,
                "max_vertex_uniform_vectors": 256,
                "max_fragment_uniform_vectors": 224,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 16
            },
            GLVersion.GL_3_3: {
                "max_texture_size": 4096,
                "max_vertex_uniform_vectors": 4096,
                "max_fragment_uniform_vectors": 1024,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 16
            },
            GLVersion.GL_4_0: {
                "max_texture_size": 8192,
                "max_vertex_uniform_vectors": 4096,
                "max_fragment_uniform_vectors": 1024,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 16
            },
            GLVersion.GL_4_3: {
                "max_texture_size": 16384,
                "max_vertex_uniform_vectors": 4096,
                "max_fragment_uniform_vectors": 1024,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 16
            }
        }
    
    def detect_version_from_shader(self, shader_source: str) -> Optional[GLVersionInfo]:
        """Detect OpenGL version from shader source code."""
        # Look for version directive
        version_match = re.search(r'#version\s+(\d+)', shader_source)
        if not version_match:
            return None
        
        glsl_version_str = version_match.group(1)
        
        # Map GLSL version to OpenGL version
        gl_version = self._glsl_to_gl_version(glsl_version_str)
        if not gl_version:
            return None
        
        # Get features and limits for this version
        features = self.version_features.get(gl_version, set())
        limits = self.version_limits.get(gl_version, {})
        
        # Find corresponding GLSL version
        glsl_version = None
        for ver in GLSLVersion:
            if ver.value == glsl_version_str:
                glsl_version = ver
                break
        
        return GLVersionInfo(
            version=gl_version,
            glsl_version=glsl_version or GLSLVersion.GLSL_110,
            features=features,
            max_texture_size=limits.get("max_texture_size", 1024),
            max_vertex_uniform_vectors=limits.get("max_vertex_uniform_vectors", 128),
            max_fragment_uniform_vectors=limits.get("max_fragment_uniform_vectors", 64),
            max_varying_vectors=limits.get("max_varying_vectors", 32),
            max_vertex_attribs=limits.get("max_vertex_attribs", 16),
            max_texture_units=limits.get("max_texture_units", 2)
        )
    
    def _glsl_to_gl_version(self, glsl_version: str) -> Optional[GLVersion]:
        """Map GLSL version to OpenGL version."""
        mapping = {
            "110": GLVersion.GL_2_0,
            "120": GLVersion.GL_2_1,
            "130": GLVersion.GL_3_0,
            "140": GLVersion.GL_3_1,
            "150": GLVersion.GL_3_2,
            "330": GLVersion.GL_3_3,
            "400": GLVersion.GL_4_0,
            "410": GLVersion.GL_4_1,
            "420": GLVersion.GL_4_2,
            "430": GLVersion.GL_4_3,
            "440": GLVersion.GL_4_4,
            "450": GLVersion.GL_4_5,
            "460": GLVersion.GL_4_6
        }
        return mapping.get(glsl_version)
    
    def check_feature_support(self, version_info: GLVersionInfo, feature: GLFeature) -> bool:
        """Check if a feature is supported in the given OpenGL version."""
        return feature in version_info.features
    
    def get_minimum_version_for_feature(self, feature: GLFeature) -> Optional[GLVersion]:
        """Get the minimum OpenGL version required for a feature."""
        for version, features in self.version_features.items():
            if feature in features:
                return version
        return None


class GLSLFeatureChecker:
    """Checks GLSL feature usage and compatibility."""
    
    def __init__(self):
        self.feature_keywords = {
            GLFeature.COMPUTE_SHADER: ["layout", "shared", "local_size"],
            GLFeature.GEOMETRY_SHADER: ["layout", "points", "lines", "triangles"],
            GLFeature.TESSELATION_SHADER: ["layout", "patch", "tessellation"],
            GLFeature.MULTIPLE_RENDER_TARGETS: ["layout", "location"],
            GLFeature.TEXTURE_ARRAYS: ["sampler2DArray", "texture2DArray"],
            GLFeature.CUBE_MAP_ARRAYS: ["samplerCubeArray", "textureCubeArray"],
            GLFeature.INSTANCED_RENDERING: ["gl_InstanceID"],
            GLFeature.TRANSFORM_FEEDBACK: ["layout", "xfb_buffer"],
            GLFeature.UNIFORM_BUFFER_OBJECTS: ["layout", "uniform", "binding"],
            GLFeature.SHADER_STORAGE_BUFFER_OBJECTS: ["layout", "buffer", "binding"],
            GLFeature.ATOMIC_COUNTERS: ["layout", "atomic_uint"],
            GLFeature.IMAGE_LOAD_STORE: ["layout", "image", "coherent"]
        }
    
    def detect_features_used(self, shader_source: str) -> Set[GLFeature]:
        """Detect which GLSL features are used in the shader."""
        used_features = set()
        
        for feature, keywords in self.feature_keywords.items():
            for keyword in keywords:
                if keyword in shader_source:
                    used_features.add(feature)
                    break
        
        return used_features
    
    def check_compatibility(self, shader_source: str, target_version: GLVersion) -> List[str]:
        """Check if shader is compatible with target OpenGL version."""
        issues = []
        
        # Detect version from shader
        detector = GLVersionDetector()
        shader_version_info = detector.detect_version_from_shader(shader_source)
        
        if not shader_version_info:
            issues.append("Could not detect GLSL version from shader")
            return issues
        
        # Check if shader version is compatible with target
        if shader_version_info.version.value > target_version.value:
            issues.append(f"Shader requires OpenGL {shader_version_info.version.value}, but target is {target_version.value}")
        
        # Check feature compatibility
        used_features = self.detect_features_used(shader_source)
        for feature in used_features:
            min_version = detector.get_minimum_version_for_feature(feature)
            if min_version and min_version.value > target_version.value:
                issues.append(f"Feature {feature.value} requires OpenGL {min_version.value}, but target is {target_version.value}")
        
        return issues


class GLPlatformUtils:
    """Platform-specific OpenGL utilities."""
    
    @staticmethod
    def get_platform_limits(platform: str) -> Dict[str, int]:
        """Get platform-specific OpenGL limits."""
        limits = {
            "desktop": {
                "max_texture_size": 16384,
                "max_vertex_uniform_vectors": 4096,
                "max_fragment_uniform_vectors": 1024,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 16
            },
            "mobile": {
                "max_texture_size": 4096,
                "max_vertex_uniform_vectors": 256,
                "max_fragment_uniform_vectors": 224,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 8
            },
            "web": {
                "max_texture_size": 4096,
                "max_vertex_uniform_vectors": 256,
                "max_fragment_uniform_vectors": 224,
                "max_varying_vectors": 32,
                "max_vertex_attribs": 16,
                "max_texture_units": 8
            }
        }
        return limits.get(platform, limits["desktop"])
    
    @staticmethod
    def get_platform_features(platform: str) -> Set[GLFeature]:
        """Get platform-specific OpenGL features."""
        features = {
            "desktop": {
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.GEOMETRY_SHADER,
                GLFeature.TESSELATION_SHADER,
                GLFeature.COMPUTE_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_ARRAYS,
                GLFeature.CUBE_MAP_ARRAYS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS,
                GLFeature.SHADER_STORAGE_BUFFER_OBJECTS,
                GLFeature.ATOMIC_COUNTERS,
                GLFeature.IMAGE_LOAD_STORE
            },
            "mobile": {
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_ARRAYS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS
            },
            "web": {
                GLFeature.SHADER_OBJECTS,
                GLFeature.VERTEX_SHADER,
                GLFeature.FRAGMENT_SHADER,
                GLFeature.MULTIPLE_RENDER_TARGETS,
                GLFeature.TEXTURE_ARRAYS,
                GLFeature.INSTANCED_RENDERING,
                GLFeature.TRANSFORM_FEEDBACK,
                GLFeature.UNIFORM_BUFFER_OBJECTS
            }
        }
        return features.get(platform, features["desktop"]) 