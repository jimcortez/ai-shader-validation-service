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
class GLSLProgram(GLSLNode):
    """Root node representing a GLSL program"""
    statements: List['GLSLStatement']

@dataclass
class GLSLStatement(GLSLNode):
    """Base class for GLSL statements"""
    pass

@dataclass
class GLSLDeclaration(GLSLStatement):
    """Variable declaration"""
    type_specifier: str
    declarators: List['GLSLDeclarator']

@dataclass
class GLSLDeclarator(GLSLNode):
    """Variable declarator"""
    name: str
    array_sizes: List['GLSLExpression']
    initializer: Optional['GLSLExpression']

@dataclass
class GLSLExpression(GLSLNode):
    """Base class for GLSL expressions"""
    pass

@dataclass
class GLSLBinaryExpression(GLSLExpression):
    """Binary expression"""
    operator: str
    left: GLSLExpression
    right: GLSLExpression

@dataclass
class GLSLUnaryExpression(GLSLExpression):
    """Unary expression"""
    operator: str
    operand: GLSLExpression

@dataclass
class GLSLIdentifier(GLSLExpression):
    """Identifier expression"""
    name: str

@dataclass
class GLSLLiteral(GLSLExpression):
    """Literal expression"""
    value: Any
    type: str

@dataclass
class GLSLFunctionCall(GLSLExpression):
    """Function call expression"""
    function: GLSLExpression
    arguments: List[GLSLExpression]

@dataclass
class GLSLArrayAccess(GLSLExpression):
    """Array access expression"""
    array: GLSLExpression
    index: GLSLExpression

@dataclass
class GLSLMemberAccess(GLSLExpression):
    """Member access expression"""
    object: GLSLExpression
    member: str

@dataclass
class GLSLCompoundStatement(GLSLStatement):
    """Compound statement (block)"""
    statements: List[GLSLStatement]

@dataclass
class GLSLIfStatement(GLSLStatement):
    """If statement"""
    condition: GLSLExpression
    then_statement: GLSLStatement
    else_statement: Optional[GLSLStatement]

@dataclass
class GLSLForStatement(GLSLStatement):
    """For statement"""
    init: Optional[GLSLStatement]
    condition: Optional[GLSLExpression]
    increment: Optional[GLSLExpression]
    body: GLSLStatement

@dataclass
class GLSLWhileStatement(GLSLStatement):
    """While statement"""
    condition: GLSLExpression
    body: GLSLStatement

@dataclass
class GLSLReturnStatement(GLSLStatement):
    """Return statement"""
    value: Optional[GLSLExpression]

@dataclass
class GLSLBreakStatement(GLSLStatement):
    """Break statement"""
    pass

@dataclass
class GLSLContinueStatement(GLSLStatement):
    """Continue statement"""
    pass

@dataclass
class GLSLDiscardStatement(GLSLStatement):
    """Discard statement"""
    pass 