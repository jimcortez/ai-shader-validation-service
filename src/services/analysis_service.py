"""
Analysis Service

This module provides comprehensive analysis capabilities for shader validation,
including error visualization, performance charts, and dependency graphs.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import json
import time
from datetime import datetime

from src.core.models.errors import ValidationError, ErrorSeverity
from src.core.renderers.error_visualizer import ErrorVisualizer, ErrorVisualizationError
from src.core.renderers.performance_charts import PerformanceCharts, PerformanceChartError
from src.core.renderers.dependency_graphs import DependencyGraphs, DependencyGraphError
from src.services.validation_service import get_validation_service
from src.services.visualization_service import get_visualization_service

logger = logging.getLogger(__name__)


class AnalysisServiceError(Exception):
    """Exception raised for analysis service errors."""
    pass


class AnalysisService:
    """
    Comprehensive analysis service for shader validation.
    
    This service integrates error visualization, performance analysis,
    and dependency analysis to provide complete shader insights.
    """
    
    def __init__(self):
        """Initialize the analysis service."""
        self.error_visualizer = ErrorVisualizer()
        self.performance_charts = PerformanceCharts()
        self.dependency_graphs = DependencyGraphs()
        self.validation_service = get_validation_service()
        self.visualization_service = get_visualization_service()
    
    def create_comprehensive_analysis(self,
                                    shader_source: str,
                                    shader_type: str,
                                    parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a comprehensive analysis of a shader.
        
        Args:
            shader_source: Shader source code or data
            shader_type: Type of shader (GLSL, ISF, MadMapper)
            parameters: Optional shader parameters
            
        Returns:
            Comprehensive analysis results
        """
        try:
            start_time = time.time()
            
            # Validate shader first
            validation_result = self.validation_service.validate_shader(
                shader_source, shader_type, parameters
            )
            
            # Extract errors and performance data
            errors = validation_result.get('errors', [])
            performance_data = validation_result.get('performance_metrics', {})
            
            # Generate visualizations
            analysis_results = {
                'validation_result': validation_result,
                'visualizations': {},
                'analysis_metadata': {
                    'analysis_time': datetime.utcnow().isoformat(),
                    'processing_time': time.time() - start_time,
                    'shader_type': shader_type,
                    'error_count': len(errors),
                    'performance_metrics_count': len(performance_data)
                }
            }
            
            # Generate error visualizations
            if errors:
                try:
                    error_report_image = self.error_visualizer.create_error_report_image(errors)
                    analysis_results['visualizations']['error_report'] = {
                        'type': 'error_report',
                        'data': error_report_image,
                        'format': 'PNG'
                    }
                except ErrorVisualizationError as e:
                    logger.warning(f"Failed to create error report: {e}")
            
            # Generate performance charts
            if performance_data:
                try:
                    performance_chart = self.performance_charts.create_performance_bar_chart(
                        performance_data, "Shader Performance Analysis"
                    )
                    analysis_results['visualizations']['performance_chart'] = {
                        'type': 'performance_chart',
                        'data': performance_chart,
                        'format': 'PNG'
                    }
                except PerformanceChartError as e:
                    logger.warning(f"Failed to create performance chart: {e}")
            
            # Generate dependency graphs if available
            structure_data = validation_result.get('structure_analysis', {})
            if structure_data:
                try:
                    dependency_graph = self.dependency_graphs.create_code_structure_graph(
                        structure_data, "Shader Code Structure"
                    )
                    analysis_results['visualizations']['dependency_graph'] = {
                        'type': 'dependency_graph',
                        'data': dependency_graph,
                        'format': 'PNG'
                    }
                except DependencyGraphError as e:
                    logger.warning(f"Failed to create dependency graph: {e}")
            
            # Generate shader visualization if no critical errors
            critical_errors = [e for e in errors if e.severity == ErrorSeverity.ERROR]
            if not critical_errors:
                try:
                    if shader_type == 'GLSL':
                        image_id, image_data = self.visualization_service.render_glsl_shader(
                            shader_source, 512, 512, parameters, 'PNG'
                        )
                    elif shader_type == 'ISF':
                        # Parse ISF data
                        if isinstance(shader_source, str):
                            isf_data = json.loads(shader_source)
                        else:
                            isf_data = shader_source
                        image_id, image_data = self.visualization_service.render_isf_shader(
                            isf_data, 512, 512, parameters, 'PNG'
                        )
                    else:
                        # Treat as GLSL
                        image_id, image_data = self.visualization_service.render_glsl_shader(
                            shader_source, 512, 512, parameters, 'PNG'
                        )
                    
                    analysis_results['visualizations']['shader_preview'] = {
                        'type': 'shader_preview',
                        'data': image_data,
                        'format': 'PNG',
                        'image_id': image_id
                    }
                    
                    # Create error overlay if there are warnings
                    warnings = [e for e in errors if e.severity == ErrorSeverity.WARNING]
                    if warnings:
                        try:
                            overlay_image = self.error_visualizer.create_error_overlay(
                                image_data, warnings, 'PNG'
                            )
                            analysis_results['visualizations']['error_overlay'] = {
                                'type': 'error_overlay',
                                'data': overlay_image,
                                'format': 'PNG'
                            }
                        except ErrorVisualizationError as e:
                            logger.warning(f"Failed to create error overlay: {e}")
                            
                except Exception as e:
                    logger.warning(f"Failed to generate shader preview: {e}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive analysis: {e}")
            raise AnalysisServiceError(f"Failed to create comprehensive analysis: {e}")
    
    def create_error_analysis_report(self, errors: List[ValidationError]) -> Dict[str, Any]:
        """
        Create a detailed error analysis report.
        
        Args:
            errors: List of validation errors
            
        Returns:
            Error analysis report
        """
        try:
            # Categorize errors
            error_categories = {}
            severity_counts = {}
            
            for error in errors:
                # Count by severity
                severity = error.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Categorize by type
                category = getattr(error, 'category', 'unknown')
                if category not in error_categories:
                    error_categories[category] = []
                error_categories[category].append(error)
            
            # Generate error report image
            error_report_image = None
            try:
                error_report_image = self.error_visualizer.create_error_report_image(errors)
            except ErrorVisualizationError as e:
                logger.warning(f"Failed to create error report image: {e}")
            
            # Generate code highlight image if we have line numbers
            code_highlight_image = None
            errors_with_lines = [e for e in errors if hasattr(e, 'line_number') and e.line_number]
            if errors_with_lines:
                try:
                    # This would need the actual shader code - for now, create a placeholder
                    placeholder_code = "// Shader code with errors\n" + "\n".join([
                        f"// Error on line {e.line_number}: {e.message}" 
                        for e in errors_with_lines[:10]
                    ])
                    code_highlight_image = self.error_visualizer.create_code_highlight_image(
                        placeholder_code, errors_with_lines
                    )
                except ErrorVisualizationError as e:
                    logger.warning(f"Failed to create code highlight image: {e}")
            
            return {
                'summary': {
                    'total_errors': len(errors),
                    'severity_breakdown': severity_counts,
                    'category_breakdown': {cat: len(errs) for cat, errs in error_categories.items()}
                },
                'categorized_errors': error_categories,
                'visualizations': {
                    'error_report': error_report_image,
                    'code_highlight': code_highlight_image
                },
                'recommendations': self._generate_error_recommendations(errors)
            }
            
        except Exception as e:
            logger.error(f"Failed to create error analysis report: {e}")
            raise AnalysisServiceError(f"Failed to create error analysis report: {e}")
    
    def create_performance_analysis_report(self, performance_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Create a detailed performance analysis report.
        
        Args:
            performance_data: Dictionary of performance metrics
            
        Returns:
            Performance analysis report
        """
        try:
            if not performance_data:
                return {
                    'summary': {'message': 'No performance data available'},
                    'visualizations': {},
                    'recommendations': []
                }
            
            # Generate performance charts
            visualizations = {}
            
            try:
                bar_chart = self.performance_charts.create_performance_bar_chart(
                    performance_data, "Performance Metrics"
                )
                visualizations['bar_chart'] = bar_chart
            except PerformanceChartError as e:
                logger.warning(f"Failed to create performance bar chart: {e}")
            
            try:
                heatmap = self.error_visualizer.create_performance_heatmap(performance_data)
                visualizations['heatmap'] = heatmap
            except ErrorVisualizationError as e:
                logger.warning(f"Failed to create performance heatmap: {e}")
            
            # Analyze performance
            analysis = self._analyze_performance_metrics(performance_data)
            
            return {
                'summary': {
                    'total_metrics': len(performance_data),
                    'metrics': performance_data,
                    'analysis': analysis
                },
                'visualizations': visualizations,
                'recommendations': self._generate_performance_recommendations(performance_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to create performance analysis report: {e}")
            raise AnalysisServiceError(f"Failed to create performance analysis report: {e}")
    
    def create_dependency_analysis_report(self, structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a detailed dependency analysis report.
        
        Args:
            structure_data: Code structure data
            
        Returns:
            Dependency analysis report
        """
        try:
            if not structure_data:
                return {
                    'summary': {'message': 'No structure data available'},
                    'visualizations': {},
                    'recommendations': []
                }
            
            # Generate dependency graphs
            visualizations = {}
            
            try:
                structure_graph = self.dependency_graphs.create_code_structure_graph(
                    structure_data, "Code Structure Analysis"
                )
                visualizations['structure_graph'] = structure_graph
            except DependencyGraphError as e:
                logger.warning(f"Failed to create structure graph: {e}")
            
            # Analyze structure
            analysis = self._analyze_code_structure(structure_data)
            
            return {
                'summary': {
                    'structure_type': structure_data.get('type', 'unknown'),
                    'complexity_score': analysis.get('complexity_score', 0),
                    'analysis': analysis
                },
                'visualizations': visualizations,
                'recommendations': self._generate_structure_recommendations(structure_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to create dependency analysis report: {e}")
            raise AnalysisServiceError(f"Failed to create dependency analysis report: {e}")
    
    def _generate_error_recommendations(self, errors: List[ValidationError]) -> List[str]:
        """Generate recommendations based on errors."""
        recommendations = []
        
        error_types = [getattr(e, 'category', 'unknown') for e in errors]
        
        if 'syntax' in error_types:
            recommendations.append("Review shader syntax and ensure all statements are properly terminated")
        
        if 'semantic' in error_types:
            recommendations.append("Check variable declarations and ensure types match their usage")
        
        if 'performance' in error_types:
            recommendations.append("Consider optimizing expensive operations and reducing texture lookups")
        
        if 'portability' in error_types:
            recommendations.append("Use standard GLSL functions and avoid vendor-specific extensions")
        
        if not recommendations:
            recommendations.append("Review the specific error messages for detailed guidance")
        
        return recommendations
    
    def _analyze_performance_metrics(self, performance_data: Dict[str, float]) -> Dict[str, Any]:
        """Analyze performance metrics."""
        if not performance_data:
            return {}
        
        analysis = {
            'overall_score': 0,
            'bottlenecks': [],
            'strengths': []
        }
        
        # Calculate overall score (simplified)
        total_score = 0
        metric_count = 0
        
        for metric, value in performance_data.items():
            # Normalize value (assuming lower is better for most metrics)
            if 'time' in metric.lower() or 'duration' in metric.lower():
                normalized = max(0, 1 - (value / 100))  # Assuming 100ms is baseline
            else:
                normalized = min(1, value / 100)  # Assuming 100 is baseline
            
            total_score += normalized
            metric_count += 1
            
            # Identify bottlenecks and strengths
            if normalized < 0.3:
                analysis['bottlenecks'].append(metric)
            elif normalized > 0.7:
                analysis['strengths'].append(metric)
        
        if metric_count > 0:
            analysis['overall_score'] = total_score / metric_count
        
        return analysis
    
    def _generate_performance_recommendations(self, performance_data: Dict[str, float]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        for metric, value in performance_data.items():
            if 'time' in metric.lower() and value > 50:
                recommendations.append(f"Optimize {metric} - current value {value:.2f} is high")
            elif 'memory' in metric.lower() and value > 100:
                recommendations.append(f"Reduce memory usage for {metric}")
        
        if not recommendations:
            recommendations.append("Performance metrics look good - continue monitoring")
        
        return recommendations
    
    def _analyze_code_structure(self, structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code structure."""
        analysis = {
            'complexity_score': 0,
            'function_count': 0,
            'variable_count': 0,
            'depth': 0
        }
        
        # Recursively count elements
        def count_elements(data, depth=0):
            if isinstance(data, dict):
                analysis['depth'] = max(analysis['depth'], depth)
                
                if data.get('type') == 'function':
                    analysis['function_count'] += 1
                elif data.get('type') == 'variable':
                    analysis['variable_count'] += 1
                
                for child in data.get('children', []):
                    count_elements(child, depth + 1)
        
        count_elements(structure_data)
        
        # Calculate complexity score
        analysis['complexity_score'] = (
            analysis['function_count'] * 2 + 
            analysis['variable_count'] + 
            analysis['depth'] * 3
        )
        
        return analysis
    
    def _generate_structure_recommendations(self, structure_data: Dict[str, Any]) -> List[str]:
        """Generate structure recommendations."""
        recommendations = []
        
        analysis = self._analyze_code_structure(structure_data)
        
        if analysis['complexity_score'] > 50:
            recommendations.append("Consider breaking down complex functions into smaller, more manageable pieces")
        
        if analysis['function_count'] > 10:
            recommendations.append("High function count detected - consider consolidating related functions")
        
        if analysis['depth'] > 5:
            recommendations.append("Deep nesting detected - consider flattening the code structure")
        
        if not recommendations:
            recommendations.append("Code structure looks well-organized")
        
        return recommendations


# Global instance
_analysis_service = None


def get_analysis_service() -> AnalysisService:
    """Get the global analysis service instance."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service 