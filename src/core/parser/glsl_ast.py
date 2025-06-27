"""
GLSL Abstract Syntax Tree representation
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GLSLNode:
    """Base class for GLSL AST nodes"""
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLProgram:
    """Root node representing a GLSL program"""
    statements: List['GLSLStatement']
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLStatement:
    """Base class for GLSL statements"""
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLDeclaration:
    """Variable declaration"""
    type_specifier: str
    declarators: List['GLSLDeclarator']
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLDeclarator:
    """Variable declarator"""
    name: str
    array_sizes: List['GLSLExpression']
    initializer: Optional['GLSLExpression']
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLExpression:
    """Base class for GLSL expressions"""
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLBinaryExpression:
    """Binary expression"""
    operator: str
    left: GLSLExpression
    right: GLSLExpression
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLUnaryExpression:
    """Unary expression"""
    operator: str
    operand: GLSLExpression
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLIdentifier:
    """Identifier expression"""
    name: str
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLLiteral:
    """Literal expression"""
    value: Any
    type: str
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLFunctionCall:
    """Function call expression"""
    function: GLSLExpression
    arguments: List[GLSLExpression]
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLArrayAccess:
    """Array access expression"""
    array: GLSLExpression
    index: GLSLExpression
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLMemberAccess:
    """Member access expression"""
    object: GLSLExpression
    member: str
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLCompoundStatement:
    """Compound statement (block)"""
    statements: List[GLSLStatement]
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLIfStatement:
    """If statement"""
    condition: GLSLExpression
    then_statement: GLSLStatement
    else_statement: Optional[GLSLStatement]
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLForStatement:
    """For statement"""
    init: Optional[GLSLStatement]
    condition: Optional[GLSLExpression]
    increment: Optional[GLSLExpression]
    body: GLSLStatement
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLWhileStatement:
    """While statement"""
    condition: GLSLExpression
    body: GLSLStatement
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLReturnStatement:
    """Return statement"""
    value: Optional[GLSLExpression]
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLBreakStatement:
    """Break statement"""
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLContinueStatement:
    """Continue statement"""
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass
class GLSLDiscardStatement:
    """Discard statement"""
    line: Optional[int] = None
    column: Optional[int] = None 