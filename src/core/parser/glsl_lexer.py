"""
GLSL lexer using Lark
"""
from lark import Lark, Token
from typing import List, Dict, Any

# GLSL grammar for Lark
GLSL_GRAMMAR = """
    ?start: program
    
    program: statement*
    
    statement: declaration
             | expression_statement
             | compound_statement
             | selection_statement
             | iteration_statement
             | jump_statement
    
    declaration: type_specifier declarator_list ";"
    
    type_specifier: "void" | "bool" | "int" | "uint" | "float" | "double"
                  | "vec2" | "vec3" | "vec4"
                  | "mat2" | "mat3" | "mat4"
                  | "sampler2D" | "samplerCube"
    
    declarator_list: declarator ("," declarator)*
    
    declarator: IDENTIFIER ("[" expression "]")* ("=" initializer)?
    
    expression_statement: expression ";"
    
    expression: assignment_expression
    
    assignment_expression: logical_or_expression
                         | unary_expression assignment_operator assignment_expression
    
    assignment_operator: "=" | "*=" | "/=" | "%=" | "+=" | "-=" | "<<=" | ">>=" | "&=" | "^=" | "|="
    
    logical_or_expression: logical_and_expression
                          | logical_or_expression "||" logical_and_expression
    
    logical_and_expression: inclusive_or_expression
                           | logical_and_expression "&&" inclusive_or_expression
    
    inclusive_or_expression: exclusive_or_expression
                            | inclusive_or_expression "|" exclusive_or_expression
    
    exclusive_or_expression: and_expression
                            | exclusive_or_expression "^" and_expression
    
    and_expression: equality_expression
                   | and_expression "&" equality_expression
    
    equality_expression: relational_expression
                        | equality_expression "==" relational_expression
                        | equality_expression "!=" relational_expression
    
    relational_expression: shift_expression
                          | relational_expression "<" shift_expression
                          | relational_expression ">" shift_expression
                          | relational_expression "<=" shift_expression
                          | relational_expression ">=" shift_expression
    
    shift_expression: additive_expression
                     | shift_expression "<<" additive_expression
                     | shift_expression ">>" additive_expression
    
    additive_expression: multiplicative_expression
                        | additive_expression "+" multiplicative_expression
                        | additive_expression "-" multiplicative_expression
    
    multiplicative_expression: unary_expression
                              | multiplicative_expression "*" unary_expression
                              | multiplicative_expression "/" unary_expression
                              | multiplicative_expression "%" unary_expression
    
    unary_expression: postfix_expression
                     | "++" unary_expression
                     | "--" unary_expression
                     | unary_operator unary_expression
    
    unary_operator: "+" | "-" | "!" | "~"
    
    postfix_expression: primary_expression
                       | postfix_expression "[" expression "]"
                       | postfix_expression "(" argument_expression_list? ")"
                       | postfix_expression "." IDENTIFIER
                       | postfix_expression "++"
                       | postfix_expression "--"
    
    primary_expression: IDENTIFIER
                       | constant
                       | "(" expression ")"
    
    constant: FLOAT_LITERAL | INT_LITERAL | BOOL_LITERAL
    
    argument_expression_list: assignment_expression ("," assignment_expression)*
    
    compound_statement: "{" statement* "}"
    
    selection_statement: "if" "(" expression ")" statement ("else" statement)?
    
    iteration_statement: "while" "(" expression ")" statement
                        | "do" statement "while" "(" expression ")" ";"
                        | "for" "(" for_init_statement for_cond_expression? ";" for_iter_expression? ")" statement
    
    for_init_statement: expression_statement | declaration
    
    for_cond_expression: expression
    
    for_iter_expression: expression
    
    jump_statement: "continue" ";"
                   | "break" ";"
                   | "return" expression? ";"
                   | "discard" ";"
    
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    FLOAT_LITERAL: /[0-9]+\.[0-9]+/
    INT_LITERAL: /[0-9]+/
    BOOL_LITERAL: "true" | "false"
    
    %import common.WS
    %ignore WS
    %import common.C_COMMENT
    %ignore C_COMMENT
    %import common.CPP_COMMENT
    %ignore CPP_COMMENT
"""

class GLSLLexer:
    """GLSL lexer using Lark"""
    
    def __init__(self):
        self.parser = Lark(GLSL_GRAMMAR, parser='earley', ambiguity='explicit')
    
    def tokenize(self, code: str) -> List[Token]:
        """Tokenize GLSL code"""
        try:
            tree = self.parser.parse(code)
            return self._extract_tokens(tree)
        except Exception as e:
            return []
    
    def _extract_tokens(self, tree) -> List[Token]:
        """Extract tokens from parse tree"""
        tokens = []
        for child in tree.children:
            if hasattr(child, 'type'):
                tokens.append(child)
            else:
                tokens.extend(self._extract_tokens(child))
        return tokens 