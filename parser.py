"""
PA 5 dependency: paste in YOUR OWN completed PA 3 parser.py here
(needed transitively -- symtable.py imports from this file).

"""
 
from dataclasses import dataclass, field
from typing import List
 
from lexer import Token, tokenize
 
 
@dataclass
class Program:
    statements: list
 
 
@dataclass
class Declaration:
    name: str
    expr: object
    line: int
 
 
@dataclass
class Assignment:
    name: str
    expr: object
    line: int
 
 
@dataclass
class BinOp:
    op: str
    left: object
    right: object
    line: int
 
 
@dataclass
class Number:
    value: int
    line: int
 
 
@dataclass
class Variable:
    name: str
    line: int
 
 
class ParseError(Exception):
    pass
 
 
class _ParserState:
    """Given: a small cursor wrapper over the token list. Not required to use, but handy."""
 
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
 
    def peek(self) -> Token:
        return self.tokens[self.pos]
 
    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok
 
    def expect(self, type_: str) -> Token:
        tok = self.peek()
        if tok.type != type_:
            raise ParseError(f"Line {tok.line}: expected {type_}, found {tok.type} ({tok.lexeme!r}).")
        return self.advance()
 
 
def parse_factor(state: _ParserState):
    # <factor> ::= NUMBER | IDENT | "-" <factor> | "(" <expr> ")"
    tok = state.peek()
    if tok.type == "NUMBER":
        state.advance()
        return Number(int(tok.lexeme), tok.line)
    if tok.type == "IDENT":
        state.advance()
        return Variable(tok.lexeme, tok.line)
    if tok.type == "MINUS":
        # Unary minus: the AST has no unary node, so -f is built as 0 - f.
        state.advance()
        operand = parse_factor(state)
        return BinOp("-", Number(0, tok.line), operand, tok.line)
    if tok.type == "LPAREN":
        state.advance()
        inner = parse_expr(state)          # arbitrary nesting via recursion
        state.expect("RPAREN")
        return inner
    raise ParseError(
        f"Line {tok.line}: expected NUMBER, IDENT, MINUS or LPAREN, "
        f"found {tok.type} ({tok.lexeme!r})."
    )
 
 
def parse_term(state: _ParserState):
    # <term> ::= <factor> { ("*" | "/") <factor> }   -- loop => left-associative
    left = parse_factor(state)
    while state.peek().type in ("STAR", "SLASH"):
        op = state.advance()
        right = parse_factor(state)
        left = BinOp(op.lexeme, left, right, op.line)
    return left
 
 
def parse_expr(state: _ParserState):
    # <expr> ::= <term> { ("+" | "-") <term> }        -- loop => left-associative
    left = parse_term(state)
    while state.peek().type in ("PLUS", "MINUS"):
        op = state.advance()
        right = parse_term(state)
        left = BinOp(op.lexeme, left, right, op.line)
    return left
 
 
def parse_declaration(state: _ParserState) -> Declaration:
    # <declaration> ::= "let" IDENT "=" <expr> ";"
    let_tok = state.expect("LET")
    name = state.expect("IDENT")
    state.expect("ASSIGN")
    expr = parse_expr(state)
    state.expect("SEMI")
    return Declaration(name.lexeme, expr, let_tok.line)
 
 
def parse_assignment(state: _ParserState) -> Assignment:
    # <assignment> ::= IDENT "=" <expr> ";"
    name = state.expect("IDENT")
    state.expect("ASSIGN")
    expr = parse_expr(state)
    state.expect("SEMI")
    return Assignment(name.lexeme, expr, name.line)
 
 
def parse_statement(state: _ParserState):
    # One token of lookahead: peek (do not consume) to pick the rule.
    tok = state.peek()
    if tok.type == "LET":
        return parse_declaration(state)
    if tok.type == "IDENT":
        return parse_assignment(state)
    raise ParseError(
        f"Line {tok.line}: expected LET or IDENT, found {tok.type} ({tok.lexeme!r})."
    )
 
 
def parse_program(state: _ParserState) -> Program:
    statements = []
    while state.peek().type != "EOF":
        statements.append(parse_statement(state))
    return Program(statements)
 
 
def parse(tokens: List[Token]) -> Program:
    state = _ParserState(tokens)
    return parse_program(state)
 