"""
Logic Flow Analyzer for GLSL Shaders

This module provides analysis of logic flow, data flow, and mathematical validation
for GLSL shaders to detect potential issues and optimization opportunities.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ast
import re

from ..parser.glsl_ast import (
    GLSLNode, GLSLProgram, GLSLStatement, GLSLExpression, 
    GLSLDeclaration, GLSLDeclarator, GLSLBinaryExpression,
    GLSLIdentifier, GLSLLiteral, GLSLFunctionCall,
    GLSLCompoundStatement, GLSLIfStatement, GLSLForStatement,
    GLSLWhileStatement, GLSLReturnStatement, GLSLBreakStatement,
    GLSLContinueStatement
)
from ..models.errors import ValidationError, ErrorSeverity


class LogicIssueType(Enum):
    """Types of logic flow issues that can be detected."""
    UNREACHABLE_CODE = "unreachable_code"
    INFINITE_LOOP = "infinite_loop"
    DEAD_CODE = "dead_code"
    UNINITIALIZED_VARIABLE = "uninitialized_variable"
    DIVISION_BY_ZERO = "division_by_zero"
    OVERFLOW_RISK = "overflow_risk"
    MISSING_RETURN = "missing_return"


@dataclass
class LogicIssue:
    """Represents a logic flow issue found during analysis."""
    issue_type: LogicIssueType
    message: str
    line: int
    column: int
    severity: ErrorSeverity
    context: Optional[str] = None
    suggestions: Optional[List[str]] = None


class LogicFlowAnalyzer:
    """Analyzes logic flow, data flow, and mathematical validation in GLSL shaders."""
    
    def __init__(self):
        self.issues: List[LogicIssue] = []
        self.variable_definitions: Dict[str, Set[int]] = {}
        self.variable_uses: Dict[str, Set[int]] = {}
        self.return_statements: Set[int] = set()
        self.break_statements: Set[int] = set()
        self.continue_statements: Set[int] = set()
        
    def analyze(self, ast_root: GLSLNode) -> List[LogicIssue]:
        """Analyze the AST for logic flow issues."""
        self.issues.clear()
        self._reset_tracking()
        
        # Perform different types of analysis
        self._analyze_data_flow(ast_root)
        self._analyze_logic_flow(ast_root)
        self._analyze_mathematical_validation(ast_root)
        self._analyze_function_returns(ast_root)
        
        return self.issues
    
    def _reset_tracking(self):
        """Reset all tracking variables."""
        self.variable_definitions.clear()
        self.variable_uses.clear()
        self.return_statements.clear()
        self.break_statements.clear()
        self.continue_statements.clear()
    
    def _analyze_data_flow(self, node: GLSLNode):
        """Analyze data flow for variable initialization and dead code."""
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                self._analyze_statement_data_flow(stmt)
        
        # Check for uninitialized variables
        for var_name, use_lines in self.variable_uses.items():
            if var_name not in self.variable_definitions:
                for line in use_lines:
                    self.issues.append(LogicIssue(
                        issue_type=LogicIssueType.UNINITIALIZED_VARIABLE,
                        message=f"Variable '{var_name}' is used but never declared",
                        line=line,
                        column=0,
                        severity=ErrorSeverity.ERROR,
                        suggestions=["Declare the variable before using it"]
                    ))
    
    def _analyze_statement_data_flow(self, stmt: GLSLStatement):
        """Analyze data flow in a single statement."""
        if isinstance(stmt, GLSLDeclaration):
            for declarator in stmt.declarators:
                if declarator.name:
                    self.variable_definitions.setdefault(declarator.name, set()).add(
                        declarator.line or 0
                    )
        
        elif isinstance(stmt, GLSLCompoundStatement):
            for child_stmt in stmt.statements:
                self._analyze_statement_data_flow(child_stmt)
        
        # Extract variable uses from expressions
        self._extract_variable_uses_from_statement(stmt)
    
    def _extract_variable_uses_from_statement(self, stmt: GLSLStatement):
        """Extract variable names used in a statement."""
        if isinstance(stmt, GLSLDeclaration):
            for declarator in stmt.declarators:
                if declarator.initializer:
                    self._extract_variable_uses_from_expression(declarator.initializer)
        
        elif isinstance(stmt, GLSLReturnStatement):
            if stmt.value:
                self._extract_variable_uses_from_expression(stmt.value)
    
    def _extract_variable_uses_from_expression(self, expr: GLSLExpression):
        """Extract variable names used in expressions."""
        if isinstance(expr, GLSLIdentifier):
            self.variable_uses.setdefault(expr.name, set()).add(expr.line or 0)
        
        elif isinstance(expr, GLSLBinaryExpression):
            self._extract_variable_uses_from_expression(expr.left)
            self._extract_variable_uses_from_expression(expr.right)
        
        elif isinstance(expr, GLSLFunctionCall):
            self._extract_variable_uses_from_expression(expr.function)
            for arg in expr.arguments:
                self._extract_variable_uses_from_expression(arg)
    
    def _analyze_logic_flow(self, node: GLSLNode):
        """Analyze logic flow for unreachable code and infinite loops."""
        if isinstance(node, GLSLProgram):
            for i, stmt in enumerate(node.statements):
                # Check for unreachable code after return/break/continue
                if self._is_terminating_statement(stmt):
                    if i + 1 < len(node.statements):
                        next_stmt = node.statements[i + 1]
                        self.issues.append(LogicIssue(
                            issue_type=LogicIssueType.UNREACHABLE_CODE,
                            message="Code after return/break/continue is unreachable",
                            line=next_stmt.line or 0,
                            column=next_stmt.column or 0,
                            severity=ErrorSeverity.WARNING,
                            suggestions=["Remove unreachable code or restructure logic"]
                        ))
                
                # Check for infinite loops
                if self._is_potential_infinite_loop(stmt):
                    self.issues.append(LogicIssue(
                        issue_type=LogicIssueType.INFINITE_LOOP,
                        message="Potential infinite loop detected",
                        line=stmt.line or 0,
                        column=stmt.column or 0,
                        severity=ErrorSeverity.WARNING,
                        suggestions=["Add a break condition or limit iterations"]
                    ))
    
    def _is_terminating_statement(self, stmt: GLSLStatement) -> bool:
        """Check if a statement is terminating (return, break, continue)."""
        return isinstance(stmt, (GLSLReturnStatement, GLSLBreakStatement, GLSLContinueStatement))
    
    def _is_potential_infinite_loop(self, stmt: GLSLStatement) -> bool:
        """Check if a statement could create an infinite loop."""
        if isinstance(stmt, GLSLWhileStatement):
            # Check if condition is always true
            if isinstance(stmt.condition, GLSLLiteral):
                if stmt.condition.value == True or stmt.condition.value == 1:
                    return True
        return False
    
    def _analyze_mathematical_validation(self, node: GLSLNode):
        """Analyze mathematical operations for potential issues."""
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                self._check_mathematical_issues_in_statement(stmt)
    
    def _check_mathematical_issues_in_statement(self, stmt: GLSLStatement):
        """Check for mathematical issues in a statement."""
        if isinstance(stmt, GLSLDeclaration):
            for declarator in stmt.declarators:
                if declarator.initializer:
                    self._check_division_by_zero(declarator.initializer)
                    self._check_overflow_risk(declarator.initializer)
        
        elif isinstance(stmt, GLSLCompoundStatement):
            for child_stmt in stmt.statements:
                self._check_mathematical_issues_in_statement(child_stmt)
    
    def _check_division_by_zero(self, expr: GLSLExpression):
        """Check for potential division by zero."""
        if isinstance(expr, GLSLBinaryExpression) and expr.operator == '/':
            if isinstance(expr.right, GLSLLiteral):
                if expr.right.value == 0:
                    self.issues.append(LogicIssue(
                        issue_type=LogicIssueType.DIVISION_BY_ZERO,
                        message="Division by zero detected",
                        line=expr.line or 0,
                        column=expr.column or 0,
                        severity=ErrorSeverity.ERROR,
                        suggestions=["Add a check to ensure divisor is not zero"]
                    ))
        
        # Recursively check child expressions
        if isinstance(expr, GLSLBinaryExpression):
            self._check_division_by_zero(expr.left)
            self._check_division_by_zero(expr.right)
    
    def _check_overflow_risk(self, expr: GLSLExpression):
        """Check for potential overflow in mathematical operations."""
        if isinstance(expr, GLSLBinaryExpression) and expr.operator in ['*', '+']:
            # Check for multiplication of large numbers
            if isinstance(expr.left, GLSLLiteral) and isinstance(expr.right, GLSLLiteral):
                left_val = expr.left.value
                right_val = expr.right.value
                
                # Simple heuristic for overflow detection
                if self._is_large_number(left_val) and self._is_large_number(right_val):
                    self.issues.append(LogicIssue(
                        issue_type=LogicIssueType.OVERFLOW_RISK,
                        message="Potential overflow in mathematical operation",
                        line=expr.line or 0,
                        column=expr.column or 0,
                        severity=ErrorSeverity.WARNING,
                        suggestions=["Consider using larger data types or checking bounds"]
                    ))
        
        # Recursively check child expressions
        if isinstance(expr, GLSLBinaryExpression):
            self._check_overflow_risk(expr.left)
            self._check_overflow_risk(expr.right)
    
    def _is_large_number(self, value) -> bool:
        """Check if a value represents a large number."""
        try:
            num = float(value)
            return abs(num) > 1000000
        except (ValueError, TypeError):
            return False
    
    def _analyze_function_returns(self, node: GLSLNode):
        """Analyze function return statements."""
        # This would be implemented when we have function definitions in the AST
        # For now, we'll focus on basic statement analysis
        pass


class DataFlowAnalyzer:
    """Analyzes data flow patterns in GLSL shaders."""
    
    def __init__(self):
        self.issues: List[LogicIssue] = []
    
    def analyze(self, ast_root: GLSLNode) -> List[LogicIssue]:
        """Analyze data flow patterns."""
        self.issues.clear()
        
        # Analyze variable scoping
        self._analyze_variable_scoping(ast_root)
        
        # Analyze dead code
        self._analyze_dead_code(ast_root)
        
        return self.issues
    
    def _analyze_variable_scoping(self, node: GLSLNode):
        """Analyze variable scoping issues."""
        # This would implement more sophisticated scoping analysis
        # For now, we'll focus on basic checks
        pass
    
    def _analyze_dead_code(self, node: GLSLNode):
        """Analyze for dead code (unused variables, unreachable code)."""
        # This would implement dead code detection
        # For now, we'll focus on basic checks
        pass


class MathematicalValidator:
    """Validates mathematical operations in GLSL shaders."""
    
    def __init__(self):
        self.issues: List[LogicIssue] = []
    
    def validate(self, ast_root: GLSLNode) -> List[LogicIssue]:
        """Validate mathematical operations."""
        self.issues.clear()
        
        # Check for mathematical issues
        self._check_mathematical_issues(ast_root)
        
        return self.issues
    
    def _check_mathematical_issues(self, node: GLSLNode):
        """Check for various mathematical issues."""
        if isinstance(node, GLSLProgram):
            for stmt in node.statements:
                self._check_precision_issues(stmt)
                self._check_numerical_stability(stmt)
    
    def _check_precision_issues(self, stmt: GLSLStatement):
        """Check for precision-related issues."""
        # This would check for mixing high and low precision qualifiers
        # For now, we'll focus on basic checks
        pass
    
    def _check_numerical_stability(self, stmt: GLSLStatement):
        """Check for numerical stability issues."""
        # This would check for potential loss of precision in calculations
        # For now, we'll focus on basic checks
        pass 