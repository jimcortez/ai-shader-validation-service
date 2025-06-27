"""
Quality Analyzer for GLSL Shaders

This module provides quality analysis including performance metrics, complexity scoring,
and best practices compliance for GLSL shaders.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math
import re

from ..parser.glsl_ast import (
    GLSLNode, GLSLProgram, GLSLStatement, GLSLExpression,
    GLSLDeclaration, GLSLDeclarator, GLSLBinaryExpression,
    GLSLIdentifier, GLSLLiteral, GLSLFunctionCall,
    GLSLCompoundStatement, GLSLIfStatement, GLSLForStatement,
    GLSLWhileStatement, GLSLReturnStatement
)
from ..models.errors import ValidationError, ErrorSeverity


class QualityMetricType(Enum):
    """Types of quality metrics that can be calculated."""
    COMPLEXITY = "complexity"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    READABILITY = "readability"
    EFFICIENCY = "efficiency"


class BestPracticeType(Enum):
    """Types of best practices that can be checked."""
    NAMING_CONVENTIONS = "naming_conventions"
    CODE_STRUCTURE = "code_structure"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    MEMORY_USAGE = "memory_usage"
    ERROR_HANDLING = "error_handling"


@dataclass
class QualityMetric:
    """Represents a quality metric measurement."""
    metric_type: QualityMetricType
    name: str
    value: float
    unit: str
    description: str
    score: float  # 0.0 to 1.0
    recommendations: Optional[List[str]] = None


@dataclass
class BestPracticeViolation:
    """Represents a best practice violation."""
    practice_type: BestPracticeType
    message: str
    line: int
    column: int
    severity: ErrorSeverity
    impact: str
    suggestions: Optional[List[str]] = None


@dataclass
class QualityReport:
    """Complete quality analysis report."""
    overall_score: float
    metrics: List[QualityMetric]
    violations: List[BestPracticeViolation]
    summary: str
    recommendations: List[str]


class QualityAnalyzer:
    """Analyzes GLSL shaders for quality metrics and best practices."""
    
    def __init__(self):
        self.metrics: List[QualityMetric] = []
        self.violations: List[BestPracticeViolation] = []
        
        # Complexity thresholds
        self.complexity_thresholds = {
            "low": 10,
            "medium": 20,
            "high": 50,
            "very_high": 100
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            "instruction_count": {"low": 100, "medium": 500, "high": 1000},
            "texture_samples": {"low": 10, "medium": 50, "high": 100},
            "branch_count": {"low": 5, "medium": 15, "high": 30}
        }
    
    def analyze(self, ast_root: GLSLNode) -> QualityReport:
        """Perform comprehensive quality analysis."""
        self.metrics.clear()
        self.violations.clear()
        
        # Calculate various metrics
        self._calculate_complexity_metrics(ast_root)
        self._calculate_performance_metrics(ast_root)
        self._calculate_maintainability_metrics(ast_root)
        self._calculate_readability_metrics(ast_root)
        
        # Check best practices
        self._check_best_practices(ast_root)
        
        # Generate overall score and recommendations
        overall_score = self._calculate_overall_score()
        summary = self._generate_summary()
        recommendations = self._generate_recommendations()
        
        return QualityReport(
            overall_score=overall_score,
            metrics=self.metrics,
            violations=self.violations,
            summary=summary,
            recommendations=recommendations
        )
    
    def _calculate_complexity_metrics(self, node: GLSLNode):
        """Calculate complexity-related metrics."""
        if isinstance(node, GLSLProgram):
            # Cyclomatic complexity
            complexity = self._calculate_cyclomatic_complexity(node)
            complexity_score = self._normalize_complexity(complexity)
            
            self.metrics.append(QualityMetric(
                metric_type=QualityMetricType.COMPLEXITY,
                name="Cyclomatic Complexity",
                value=complexity,
                unit="",
                description="Measures the number of linearly independent paths through the code",
                score=complexity_score,
                recommendations=self._get_complexity_recommendations(complexity)
            ))
            
            # Nesting depth
            max_depth = self._calculate_max_nesting_depth(node)
            depth_score = self._normalize_depth(max_depth)
            
            self.metrics.append(QualityMetric(
                metric_type=QualityMetricType.COMPLEXITY,
                name="Maximum Nesting Depth",
                value=max_depth,
                unit="levels",
                description="Maximum depth of nested control structures",
                score=depth_score,
                recommendations=self._get_depth_recommendations(max_depth)
            ))
    
    def _calculate_cyclomatic_complexity(self, node: GLSLNode) -> int:
        """Calculate cyclomatic complexity of the shader."""
        complexity = 1  # Base complexity
        
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                complexity += self._get_statement_complexity(stmt)
        
        return complexity
    
    def _get_statement_complexity(self, stmt: GLSLStatement) -> int:
        """Get complexity contribution of a single statement."""
        if isinstance(stmt, GLSLIfStatement):
            return 1
        elif isinstance(stmt, GLSLForStatement):
            return 1
        elif isinstance(stmt, GLSLWhileStatement):
            return 1
        elif isinstance(stmt, GLSLCompoundStatement):
            complexity = 0
            for child_stmt in stmt.statements:
                complexity += self._get_statement_complexity(child_stmt)
            return complexity
        return 0
    
    def _normalize_complexity(self, complexity: int) -> float:
        """Normalize complexity to a 0-1 score (lower is better)."""
        if complexity <= self.complexity_thresholds["low"]:
            return 1.0
        elif complexity <= self.complexity_thresholds["medium"]:
            return 0.8
        elif complexity <= self.complexity_thresholds["high"]:
            return 0.5
        elif complexity <= self.complexity_thresholds["very_high"]:
            return 0.2
        else:
            return 0.0
    
    def _calculate_max_nesting_depth(self, node: GLSLNode) -> int:
        """Calculate maximum nesting depth of control structures."""
        if isinstance(node, GLSLProgram):
            max_depth = 0
            for stmt in node.statements:
                depth = self._get_statement_depth(stmt, 0)
                max_depth = max(max_depth, depth)
            return max_depth
        return 0
    
    def _get_statement_depth(self, stmt: GLSLStatement, current_depth: int) -> int:
        """Get the depth of a statement and its children."""
        max_depth = current_depth
        
        if isinstance(stmt, GLSLIfStatement):
            max_depth = max(max_depth, self._get_statement_depth(stmt.then_statement, current_depth + 1))
            if stmt.else_statement:
                max_depth = max(max_depth, self._get_statement_depth(stmt.else_statement, current_depth + 1))
        elif isinstance(stmt, GLSLForStatement):
            max_depth = max(max_depth, self._get_statement_depth(stmt.body, current_depth + 1))
        elif isinstance(stmt, GLSLWhileStatement):
            max_depth = max(max_depth, self._get_statement_depth(stmt.body, current_depth + 1))
        elif isinstance(stmt, GLSLCompoundStatement):
            for child_stmt in stmt.statements:
                max_depth = max(max_depth, self._get_statement_depth(child_stmt, current_depth))
        
        return max_depth
    
    def _normalize_depth(self, depth: int) -> float:
        """Normalize nesting depth to a 0-1 score (lower is better)."""
        if depth <= 3:
            return 1.0
        elif depth <= 5:
            return 0.8
        elif depth <= 7:
            return 0.5
        elif depth <= 10:
            return 0.2
        else:
            return 0.0
    
    def _calculate_performance_metrics(self, node: GLSLNode):
        """Calculate performance-related metrics."""
        if isinstance(node, GLSLProgram):
            # Instruction count estimation
            instruction_count = self._estimate_instruction_count(node)
            instruction_score = self._normalize_instruction_count(instruction_count)
            
            self.metrics.append(QualityMetric(
                metric_type=QualityMetricType.PERFORMANCE,
                name="Estimated Instruction Count",
                value=instruction_count,
                unit="instructions",
                description="Estimated number of GPU instructions",
                score=instruction_score,
                recommendations=self._get_instruction_recommendations(instruction_count)
            ))
            
            # Texture sample count
            texture_samples = self._count_texture_samples(node)
            texture_score = self._normalize_texture_samples(texture_samples)
            
            self.metrics.append(QualityMetric(
                metric_type=QualityMetricType.PERFORMANCE,
                name="Texture Sample Count",
                value=texture_samples,
                unit="samples",
                description="Number of texture sampling operations",
                score=texture_score,
                recommendations=self._get_texture_recommendations(texture_samples)
            ))
    
    def _estimate_instruction_count(self, node: GLSLNode) -> int:
        """Estimate the number of GPU instructions."""
        count = 0
        
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                count += self._get_statement_instruction_count(stmt)
        
        return count
    
    def _get_statement_instruction_count(self, stmt: GLSLStatement) -> int:
        """Estimate instruction count for a statement."""
        if isinstance(stmt, GLSLDeclaration):
            return 1  # Variable declaration
        elif isinstance(stmt, GLSLCompoundStatement):
            count = 0
            for child_stmt in stmt.statements:
                count += self._get_statement_instruction_count(child_stmt)
            return count
        elif isinstance(stmt, GLSLIfStatement):
            return 2 + self._get_statement_instruction_count(stmt.then_statement)
        elif isinstance(stmt, GLSLForStatement):
            return 3 + self._get_statement_instruction_count(stmt.body)
        elif isinstance(stmt, GLSLWhileStatement):
            return 2 + self._get_statement_instruction_count(stmt.body)
        elif isinstance(stmt, GLSLReturnStatement):
            return 1
        else:
            return 1  # Default for other statements
    
    def _normalize_instruction_count(self, count: int) -> float:
        """Normalize instruction count to a 0-1 score (lower is better)."""
        thresholds = self.performance_thresholds["instruction_count"]
        if count <= thresholds["low"]:
            return 1.0
        elif count <= thresholds["medium"]:
            return 0.7
        elif count <= thresholds["high"]:
            return 0.3
        else:
            return 0.0
    
    def _count_texture_samples(self, node: GLSLNode) -> int:
        """Count texture sampling operations."""
        count = 0
        
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                count += self._get_statement_texture_count(stmt)
        
        return count
    
    def _get_statement_texture_count(self, stmt: GLSLStatement) -> int:
        """Count texture samples in a statement."""
        if isinstance(stmt, GLSLCompoundStatement):
            count = 0
            for child_stmt in stmt.statements:
                count += self._get_statement_texture_count(child_stmt)
            return count
        # This would check for texture function calls
        # For now, return 0 as placeholder
        return 0
    
    def _normalize_texture_samples(self, count: int) -> float:
        """Normalize texture sample count to a 0-1 score (lower is better)."""
        thresholds = self.performance_thresholds["texture_samples"]
        if count <= thresholds["low"]:
            return 1.0
        elif count <= thresholds["medium"]:
            return 0.7
        elif count <= thresholds["high"]:
            return 0.3
        else:
            return 0.0
    
    def _calculate_maintainability_metrics(self, node: GLSLNode):
        """Calculate maintainability-related metrics."""
        if isinstance(node, GLSLProgram):
            # Function count (would be implemented when we have function parsing)
            function_count = 0
            maintainability_score = 1.0 if function_count <= 5 else 0.5
            
            self.metrics.append(QualityMetric(
                metric_type=QualityMetricType.MAINTAINABILITY,
                name="Function Count",
                value=function_count,
                unit="functions",
                description="Number of user-defined functions",
                score=maintainability_score,
                recommendations=["Keep functions small and focused"] if function_count > 5 else None
            ))
    
    def _calculate_readability_metrics(self, node: GLSLNode):
        """Calculate readability-related metrics."""
        if isinstance(node, GLSLProgram):
            # Line count
            line_count = self._estimate_line_count(node)
            readability_score = 1.0 if line_count <= 100 else 0.7 if line_count <= 300 else 0.3
            
            self.metrics.append(QualityMetric(
                metric_type=QualityMetricType.READABILITY,
                name="Estimated Line Count",
                value=line_count,
                unit="lines",
                description="Estimated number of code lines",
                score=readability_score,
                recommendations=["Consider breaking into smaller shaders"] if line_count > 300 else None
            ))
    
    def _estimate_line_count(self, node: GLSLNode) -> int:
        """Estimate the number of code lines."""
        # This would be more sophisticated in a real implementation
        # For now, return a placeholder
        return 50
    
    def _check_best_practices(self, node: GLSLNode):
        """Check for best practice violations."""
        if isinstance(node, GLSLProgram):
            self._check_naming_conventions(node)
            self._check_code_structure(node)
            self._check_performance_optimizations(node)
    
    def _check_naming_conventions(self, node: GLSLNode):
        """Check naming convention compliance."""
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                if isinstance(stmt, GLSLDeclaration):
                    for declarator in stmt.declarators:
                        if declarator.name and not self._follows_naming_convention(declarator.name):
                            self.violations.append(BestPracticeViolation(
                                practice_type=BestPracticeType.NAMING_CONVENTIONS,
                                message=f"Variable '{declarator.name}' doesn't follow naming conventions",
                                line=declarator.line or 0,
                                column=declarator.column or 0,
                                severity=ErrorSeverity.WARNING,
                                impact="Reduces code readability",
                                suggestions=["Use camelCase for variables", "Use descriptive names"]
                            ))
    
    def _follows_naming_convention(self, name: str) -> bool:
        """Check if a name follows GLSL naming conventions."""
        # Check for camelCase or snake_case
        return bool(re.match(r'^[a-z][a-zA-Z0-9_]*$', name))
    
    def _check_code_structure(self, node: GLSLNode):
        """Check code structure best practices."""
        if isinstance(node, GLSLProgram):
            # Check for excessive nesting
            max_depth = self._calculate_max_nesting_depth(node)
            if max_depth > 5:
                self.violations.append(BestPracticeViolation(
                    practice_type=BestPracticeType.CODE_STRUCTURE,
                    message=f"Excessive nesting depth ({max_depth} levels)",
                    line=0,
                    column=0,
                    severity=ErrorSeverity.WARNING,
                    impact="Reduces code readability and maintainability",
                    suggestions=["Extract complex logic into functions", "Use early returns"]
                ))
    
    def _check_performance_optimizations(self, node: GLSLNode):
        """Check for performance optimization opportunities."""
        if isinstance(node, GLSLProgram):
            # Check for expensive operations in loops
            if self._has_expensive_operations_in_loops(node):
                self.violations.append(BestPracticeViolation(
                    practice_type=BestPracticeType.PERFORMANCE_OPTIMIZATION,
                    message="Expensive operations detected in loops",
                    line=0,
                    column=0,
                    severity=ErrorSeverity.WARNING,
                    impact="May cause performance issues",
                    suggestions=["Move expensive operations outside loops", "Use loop unrolling where appropriate"]
                ))
    
    def _has_expensive_operations_in_loops(self, node: GLSLNode) -> bool:
        """Check if there are expensive operations inside loops."""
        # This would implement loop analysis
        # For now, return False as placeholder
        return False
    
    def _calculate_overall_score(self) -> float:
        """Calculate overall quality score."""
        if not self.metrics:
            return 0.0
        
        # Weighted average of all metric scores
        total_weight = 0
        weighted_sum = 0
        
        for metric in self.metrics:
            weight = self._get_metric_weight(metric.metric_type)
            weighted_sum += metric.score * weight
            total_weight += weight
        
        # Penalize for violations
        violation_penalty = len(self.violations) * 0.05
        final_score = (weighted_sum / total_weight) - violation_penalty
        
        return max(0.0, min(1.0, final_score))
    
    def _get_metric_weight(self, metric_type: QualityMetricType) -> float:
        """Get weight for a metric type in overall score calculation."""
        weights = {
            QualityMetricType.COMPLEXITY: 0.3,
            QualityMetricType.PERFORMANCE: 0.3,
            QualityMetricType.MAINTAINABILITY: 0.2,
            QualityMetricType.READABILITY: 0.2
        }
        return weights.get(metric_type, 0.1)
    
    def _generate_summary(self) -> str:
        """Generate a summary of the quality analysis."""
        if not self.metrics and not self.violations:
            return "No quality issues detected."
        
        summary_parts = []
        
        if self.metrics:
            summary_parts.append(f"Quality metrics calculated: {len(self.metrics)}")
        
        if self.violations:
            summary_parts.append(f"Best practice violations: {len(self.violations)}")
        
        return "; ".join(summary_parts)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate overall recommendations."""
        recommendations = []
        
        # Collect recommendations from metrics
        for metric in self.metrics:
            if metric.recommendations:
                recommendations.extend(metric.recommendations)
        
        # Collect recommendations from violations
        for violation in self.violations:
            if violation.suggestions:
                recommendations.extend(violation.suggestions)
        
        # Remove duplicates and return
        return list(set(recommendations))
    
    def _get_complexity_recommendations(self, complexity: int) -> List[str]:
        """Get recommendations based on complexity."""
        if complexity > self.complexity_thresholds["high"]:
            return ["Consider breaking the shader into smaller functions", "Simplify control flow"]
        elif complexity > self.complexity_thresholds["medium"]:
            return ["Monitor complexity as the shader grows"]
        return []
    
    def _get_depth_recommendations(self, depth: int) -> List[str]:
        """Get recommendations based on nesting depth."""
        if depth > 7:
            return ["Extract deeply nested logic into functions", "Use early returns to reduce nesting"]
        elif depth > 5:
            return ["Consider reducing nesting depth for better readability"]
        return []
    
    def _get_instruction_recommendations(self, count: int) -> List[str]:
        """Get recommendations based on instruction count."""
        thresholds = self.performance_thresholds["instruction_count"]
        if count > thresholds["high"]:
            return ["Consider splitting into multiple passes", "Optimize expensive operations"]
        elif count > thresholds["medium"]:
            return ["Monitor performance on target hardware"]
        return []
    
    def _get_texture_recommendations(self, count: int) -> List[str]:
        """Get recommendations based on texture sample count."""
        thresholds = self.performance_thresholds["texture_samples"]
        if count > thresholds["high"]:
            return ["Consider texture atlasing", "Use texture arrays where possible"]
        elif count > thresholds["medium"]:
            return ["Monitor texture cache performance"]
        return [] 