"""
Machine Learning Analyzer

This module provides machine learning-based analysis for shader validation,
including error detection, fix suggestions, and optimization recommendations.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import re
import json
from dataclasses import dataclass

from src.core.models.errors import ValidationError, ErrorSeverity

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """Machine learning prediction result."""
    confidence: float
    prediction_type: str
    details: Dict[str, Any]
    suggestions: List[str]


class MLAnalyzerError(Exception):
    """Exception raised for ML analyzer errors."""
    pass


class MLAnalyzer:
    """
    Machine learning-based analyzer for shader validation.
    
    This class provides ML-powered analysis for error detection,
    fix suggestions, and optimization recommendations.
    """
    
    def __init__(self):
        """Initialize the ML analyzer."""
        self.error_patterns = self._load_error_patterns()
        self.optimization_patterns = self._load_optimization_patterns()
        self.fix_suggestions = self._load_fix_suggestions()
        
        # Performance thresholds (could be learned from data)
        self.performance_thresholds = {
            'texture_lookups': 10,
            'arithmetic_operations': 100,
            'conditional_statements': 20,
            'loop_iterations': 50
        }
    
    def analyze_shader_ml(self, shader_code: str, shader_type: str = 'GLSL') -> Dict[str, Any]:
        """
        Perform machine learning-based analysis on shader code.
        
        Args:
            shader_code: Shader source code
            shader_type: Type of shader
            
        Returns:
            ML analysis results
        """
        try:
            results = {
                'error_predictions': [],
                'optimization_suggestions': [],
                'fix_suggestions': [],
                'quality_score': 0.0,
                'confidence_metrics': {}
            }
            
            # Extract features
            features = self._extract_features(shader_code, shader_type)
            
            # Predict errors
            error_predictions = self._predict_errors(shader_code, features)
            results['error_predictions'] = error_predictions
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(features)
            results['optimization_suggestions'] = optimization_suggestions
            
            # Generate fix suggestions
            fix_suggestions = self._generate_fix_suggestions(shader_code, error_predictions)
            results['fix_suggestions'] = fix_suggestions
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(features, error_predictions)
            results['quality_score'] = quality_score
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(features, error_predictions)
            results['confidence_metrics'] = confidence_metrics
            
            return results
            
        except Exception as e:
            logger.error(f"Error in ML analysis: {e}")
            raise MLAnalyzerError(f"ML analysis failed: {e}")
    
    def predict_errors(self, shader_code: str) -> List[MLPrediction]:
        """
        Predict potential errors in shader code.
        
        Args:
            shader_code: Shader source code
            
        Returns:
            List of error predictions
        """
        try:
            predictions = []
            
            # Check for common error patterns
            for pattern_name, pattern_info in self.error_patterns.items():
                pattern = pattern_info['pattern']
                matches = re.finditer(pattern, shader_code, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    confidence = self._calculate_pattern_confidence(match, pattern_info)
                    
                    prediction = MLPrediction(
                        confidence=confidence,
                        prediction_type='error',
                        details={
                            'pattern': pattern_name,
                            'line_number': shader_code[:match.start()].count('\n') + 1,
                            'column_number': match.start() - shader_code.rfind('\n', 0, match.start()),
                            'matched_text': match.group(),
                            'severity': pattern_info.get('severity', 'warning')
                        },
                        suggestions=pattern_info.get('suggestions', [])
                    )
                    predictions.append(prediction)
            
            # Check for performance issues
            performance_predictions = self._predict_performance_issues(shader_code)
            predictions.extend(performance_predictions)
            
            # Check for compatibility issues
            compatibility_predictions = self._predict_compatibility_issues(shader_code)
            predictions.extend(compatibility_predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting errors: {e}")
            raise MLAnalyzerError(f"Error prediction failed: {e}")
    
    def suggest_optimizations(self, shader_code: str) -> List[MLPrediction]:
        """
        Suggest optimizations for shader code.
        
        Args:
            shader_code: Shader source code
            
        Returns:
            List of optimization suggestions
        """
        try:
            suggestions = []
            features = self._extract_features(shader_code)
            
            # Check optimization patterns
            for pattern_name, pattern_info in self.optimization_patterns.items():
                pattern = pattern_info['pattern']
                matches = re.finditer(pattern, shader_code, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    confidence = self._calculate_optimization_confidence(match, pattern_info, features)
                    
                    if confidence > 0.5:  # Only suggest if confidence is high enough
                        suggestion = MLPrediction(
                            confidence=confidence,
                            prediction_type='optimization',
                            details={
                                'pattern': pattern_name,
                                'line_number': shader_code[:match.start()].count('\n') + 1,
                                'column_number': match.start() - shader_code.rfind('\n', 0, match.start()),
                                'matched_text': match.group(),
                                'potential_improvement': pattern_info.get('improvement', 'unknown')
                            },
                            suggestions=pattern_info.get('suggestions', [])
                        )
                        suggestions.append(suggestion)
            
            # Generate performance-based suggestions
            performance_suggestions = self._generate_performance_suggestions(features)
            suggestions.extend(performance_suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting optimizations: {e}")
            raise MLAnalyzerError(f"Optimization suggestion failed: {e}")
    
    def generate_fix_suggestions(self, error_predictions: List[MLPrediction]) -> List[Dict[str, Any]]:
        """
        Generate fix suggestions for predicted errors.
        
        Args:
            error_predictions: List of error predictions
            
        Returns:
            List of fix suggestions
        """
        try:
            fixes = []
            
            for prediction in error_predictions:
                if prediction.prediction_type == 'error':
                    pattern_name = prediction.details['pattern']
                    
                    if pattern_name in self.fix_suggestions:
                        fix_info = self.fix_suggestions[pattern_name]
                        
                        fix = {
                            'error_type': pattern_name,
                            'line_number': prediction.details['line_number'],
                            'column_number': prediction.details['column_number'],
                            'description': fix_info.get('description', ''),
                            'suggested_fix': fix_info.get('fix', ''),
                            'confidence': prediction.confidence,
                            'examples': fix_info.get('examples', [])
                        }
                        fixes.append(fix)
            
            return fixes
            
        except Exception as e:
            logger.error(f"Error generating fix suggestions: {e}")
            raise MLAnalyzerError(f"Fix suggestion generation failed: {e}")
    
    def _extract_features(self, shader_code: str, shader_type: str = 'GLSL') -> Dict[str, Any]:
        """Extract features from shader code for ML analysis."""
        features = {
            'total_lines': len(shader_code.split('\n')),
            'total_characters': len(shader_code),
            'function_count': len(re.findall(r'\b\w+\s+\w+\s*\([^)]*\)\s*\{', shader_code)),
            'variable_declarations': len(re.findall(r'\b(?:uniform|varying|attribute|in|out)\s+\w+', shader_code)),
            'texture_lookups': len(re.findall(r'\btexture2D\s*\(', shader_code)),
            'arithmetic_operations': len(re.findall(r'[\+\-\*/]', shader_code)),
            'conditional_statements': len(re.findall(r'\b(?:if|else|switch)\b', shader_code)),
            'loop_statements': len(re.findall(r'\b(?:for|while|do)\b', shader_code)),
            'builtin_functions': len(re.findall(r'\b(?:sin|cos|tan|pow|sqrt|length|normalize)\s*\(', shader_code)),
            'comments': len(re.findall(r'//.*$|/\*.*?\*/', shader_code, re.MULTILINE | re.DOTALL)),
            'complexity_score': 0
        }
        
        # Calculate complexity score
        features['complexity_score'] = (
            features['function_count'] * 2 +
            features['conditional_statements'] * 1.5 +
            features['loop_statements'] * 2 +
            features['texture_lookups'] * 0.5
        )
        
        return features
    
    def _predict_errors(self, shader_code: str, features: Dict[str, Any]) -> List[MLPrediction]:
        """Predict errors based on code patterns and features."""
        predictions = []
        
        # Check for common error patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            pattern = pattern_info['pattern']
            matches = re.finditer(pattern, shader_code, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                confidence = self._calculate_pattern_confidence(match, pattern_info)
                
                prediction = MLPrediction(
                    confidence=confidence,
                    prediction_type='error',
                    details={
                        'pattern': pattern_name,
                        'line_number': shader_code[:match.start()].count('\n') + 1,
                        'column_number': match.start() - shader_code.rfind('\n', 0, match.start()),
                        'matched_text': match.group(),
                        'severity': pattern_info.get('severity', 'warning')
                    },
                    suggestions=pattern_info.get('suggestions', [])
                )
                predictions.append(prediction)
        
        return predictions
    
    def _generate_optimization_suggestions(self, features: Dict[str, Any]) -> List[MLPrediction]:
        """Generate optimization suggestions based on features."""
        suggestions = []
        
        # Check performance thresholds
        for metric, threshold in self.performance_thresholds.items():
            if metric in features and features[metric] > threshold:
                confidence = min(1.0, features[metric] / (threshold * 2))
                
                suggestion = MLPrediction(
                    confidence=confidence,
                    prediction_type='optimization',
                    details={
                        'metric': metric,
                        'current_value': features[metric],
                        'threshold': threshold,
                        'improvement_potential': 'high' if confidence > 0.8 else 'medium'
                    },
                    suggestions=self._get_optimization_suggestions(metric, features[metric])
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_fix_suggestions(self, shader_code: str, error_predictions: List[MLPrediction]) -> List[Dict[str, Any]]:
        """Generate fix suggestions for errors."""
        fixes = []
        
        for prediction in error_predictions:
            if prediction.prediction_type == 'error':
                pattern_name = prediction.details['pattern']
                
                if pattern_name in self.fix_suggestions:
                    fix_info = self.fix_suggestions[pattern_name]
                    
                    fix = {
                        'error_type': pattern_name,
                        'line_number': prediction.details['line_number'],
                        'column_number': prediction.details['column_number'],
                        'description': fix_info.get('description', ''),
                        'suggested_fix': fix_info.get('fix', ''),
                        'confidence': prediction.confidence,
                        'examples': fix_info.get('examples', [])
                    }
                    fixes.append(fix)
        
        return fixes
    
    def _calculate_quality_score(self, features: Dict[str, Any], error_predictions: List[MLPrediction]) -> float:
        """Calculate overall quality score."""
        base_score = 100.0
        
        # Deduct points for errors
        error_penalty = sum(pred.confidence * 10 for pred in error_predictions if pred.prediction_type == 'error')
        
        # Deduct points for complexity
        complexity_penalty = min(20.0, features['complexity_score'] * 2)
        
        # Deduct points for performance issues
        performance_penalty = 0
        for metric, threshold in self.performance_thresholds.items():
            if metric in features and features[metric] > threshold:
                performance_penalty += min(10.0, (features[metric] - threshold) / threshold * 5)
        
        quality_score = max(0.0, base_score - error_penalty - complexity_penalty - performance_penalty)
        return quality_score / 100.0  # Normalize to 0-1
    
    def _calculate_confidence_metrics(self, features: Dict[str, Any], error_predictions: List[MLPrediction]) -> Dict[str, float]:
        """Calculate confidence metrics for the analysis."""
        return {
            'feature_completeness': min(1.0, len(features) / 15.0),
            'error_confidence': sum(pred.confidence for pred in error_predictions) / max(1, len(error_predictions)),
            'code_complexity': min(1.0, features['complexity_score'] / 50.0),
            'overall_confidence': 0.8  # Base confidence for ML analysis
        }
    
    def _predict_performance_issues(self, shader_code: str) -> List[MLPrediction]:
        """Predict performance issues in shader code."""
        predictions = []
        
        # Check for expensive operations
        expensive_patterns = {
            'multiple_texture_lookups': r'texture2D\s*\([^)]*\)\s*\.\s*\w+\s*\.\s*\w+',
            'nested_conditionals': r'if\s*\([^)]*\)\s*\{[^}]*if\s*\([^)]*\)',
            'unbounded_loops': r'for\s*\([^)]*\)\s*\{[^}]*\}',
            'expensive_functions': r'\b(?:pow|sqrt|length|normalize)\s*\([^)]*\)'
        }
        
        for pattern_name, pattern in expensive_patterns.items():
            matches = re.finditer(pattern, shader_code, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                prediction = MLPrediction(
                    confidence=0.7,
                    prediction_type='performance_issue',
                    details={
                        'pattern': pattern_name,
                        'line_number': shader_code[:match.start()].count('\n') + 1,
                        'matched_text': match.group()
                    },
                    suggestions=[f"Consider optimizing {pattern_name} for better performance"]
                )
                predictions.append(prediction)
        
        return predictions
    
    def _predict_compatibility_issues(self, shader_code: str) -> List[MLPrediction]:
        """Predict compatibility issues in shader code."""
        predictions = []
        
        # Check for non-standard extensions
        extension_patterns = {
            'vendor_specific': r'#extension\s+\w+_',
            'non_standard_functions': r'\b(?:gl_FragColor|gl_FragData)\b',
            'deprecated_features': r'\b(?:varying|attribute)\b'
        }
        
        for pattern_name, pattern in extension_patterns.items():
            matches = re.finditer(pattern, shader_code, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                prediction = MLPrediction(
                    confidence=0.8,
                    prediction_type='compatibility_issue',
                    details={
                        'pattern': pattern_name,
                        'line_number': shader_code[:match.start()].count('\n') + 1,
                        'matched_text': match.group()
                    },
                    suggestions=[f"Consider using standard {pattern_name} for better compatibility"]
                )
                predictions.append(prediction)
        
        return predictions
    
    def _calculate_pattern_confidence(self, match, pattern_info: Dict[str, Any]) -> float:
        """Calculate confidence for a pattern match."""
        base_confidence = pattern_info.get('base_confidence', 0.5)
        
        # Adjust confidence based on match context
        matched_text = match.group()
        if len(matched_text) > 10:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _calculate_optimization_confidence(self, match, pattern_info: Dict[str, Any], features: Dict[str, Any]) -> float:
        """Calculate confidence for optimization suggestions."""
        base_confidence = pattern_info.get('base_confidence', 0.5)
        
        # Adjust based on code complexity
        if features['complexity_score'] > 20:
            base_confidence += 0.2
        
        return min(1.0, base_confidence)
    
    def _get_optimization_suggestions(self, metric: str, value: int) -> List[str]:
        """Get optimization suggestions for a specific metric."""
        suggestions = {
            'texture_lookups': [
                "Consider using texture atlases to reduce texture lookups",
                "Cache texture lookups in variables when used multiple times",
                "Use texture arrays instead of multiple individual textures"
            ],
            'arithmetic_operations': [
                "Simplify mathematical expressions",
                "Use built-in functions where possible",
                "Consider using lookup tables for expensive calculations"
            ],
            'conditional_statements': [
                "Combine multiple conditions where possible",
                "Use early returns to reduce nesting",
                "Consider using step() or smoothstep() functions"
            ],
            'loop_iterations': [
                "Limit loop iterations to a reasonable maximum",
                "Consider unrolling small loops",
                "Use loop-invariant code motion"
            ]
        }
        
        return suggestions.get(metric, ["Consider optimizing this aspect of the shader"])
    
    def _load_error_patterns(self) -> Dict[str, Any]:
        """Load error detection patterns."""
        return {
            'undefined_variable': {
                'pattern': r'\b\w+\s*[=+\-*/]\s*\b(?!uniform|varying|attribute|in|out|const)\w+\b',
                'severity': 'error',
                'base_confidence': 0.7,
                'suggestions': ['Declare the variable before using it']
            },
            'missing_semicolon': {
                'pattern': r'[^;]\s*\n\s*(?:uniform|varying|attribute|in|out|const)',
                'severity': 'error',
                'base_confidence': 0.8,
                'suggestions': ['Add semicolon at the end of the statement']
            },
            'unmatched_brackets': {
                'pattern': r'\{[^{}]*$',
                'severity': 'error',
                'base_confidence': 0.9,
                'suggestions': ['Check for unmatched opening braces']
            }
        }
    
    def _load_optimization_patterns(self) -> Dict[str, Any]:
        """Load optimization detection patterns."""
        return {
            'redundant_calculations': {
                'pattern': r'(\w+)\s*=\s*([^;]+);\s*\1\s*=\s*\2',
                'improvement': 'medium',
                'base_confidence': 0.6,
                'suggestions': ['Remove redundant assignment']
            },
            'expensive_operations': {
                'pattern': r'pow\s*\([^,]+,\s*2\.0\)',
                'improvement': 'high',
                'base_confidence': 0.8,
                'suggestions': ['Use multiplication instead of pow(x, 2.0)']
            }
        }
    
    def _load_fix_suggestions(self) -> Dict[str, Any]:
        """Load fix suggestions for common errors."""
        return {
            'undefined_variable': {
                'description': 'Variable used before declaration',
                'fix': 'Add variable declaration before use',
                'examples': ['float myVar = 1.0;']
            },
            'missing_semicolon': {
                'description': 'Missing semicolon at end of statement',
                'fix': 'Add semicolon at the end of the statement',
                'examples': ['uniform float time;']
            },
            'unmatched_brackets': {
                'description': 'Unmatched opening brace',
                'fix': 'Add closing brace or remove extra opening brace',
                'examples': ['void main() { /* code */ }']
            }
        } 