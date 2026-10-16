"""
PA 5 dependency: paste in YOUR OWN completed PA 2 lexer.py here.
(Needed transitively -- symtable.py imports from parser.py, which
imports from this file. PA 5's own new work doesn't touch lexing or
parsing directly.)

This is the same file from PA 2's repo -- copy your own working
tokenize() implementation over this stub before starting parser.py.
Every PA repo is independent (no shared filesystem across repos), so
each pipeline stage bundles its own copy of the prior stages.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    lexeme: str
    line: int


class LexError(Exception):
    pass


# TODO: build your master regex here, e.g.:
# _MASTER_RE = re.compile(r"(?P<NUMBER>\d+)|(?P<IDENT>[A-Za-z_]\w*)|...")
_MASTER_RE = re.compile(
    r"(?P<NUMBER>[0-9]+)"
    r"|(?P<IDENT>[A-Za-z][A-Za-z0-9]*)"
    r"|(?P<WHITESPACE>[ \t\r\n]+)"
    r"|(?P<COMMENT>\#[^\r\n]*)"
    r"|(?P<PLUS>\+)"
    r"|(?P<MINUS>-)"
    r"|(?P<STAR>\*)"
    r"|(?P<SLASH>/)"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<ASSIGN>=)"
    r"|(?P<SEMI>;)"
)

def tokenize(source: str) -> List[Token]:
    """
    Convert `source` into a list of Token objects, ending in an EOF
    token with an empty lexeme. Recognize NUMBER, IDENT, LET, PLUS,
    MINUS, STAR, SLASH, LPAREN, RPAREN, ASSIGN, SEMI. Discard
    whitespace and '#'-prefixed comments without emitting tokens for
    them. Track 1-indexed line numbers. Raise LexError (with the
    offending character and line) on unrecognized input.
    """
    # TODO
    tokens = []
    position = 0
    line = 1
    while position < len(source):
        match = _MASTER_RE.match(source, position)
        if match is None:
            raise LexError(
                f"Unexpected character {source[position]!r} on line {line}"
            )
        
        token_type = match.lastgroup
        lexeme = match.group()

        position = match.end()

        if token_type == "WHITESPACE" or token_type == "COMMENT":
            line += lexeme.count("\n")
            continue
        
        if token_type == "IDENT" and lexeme == "let":
            token_type = "LET"

        tokens.append(Token(token_type, lexeme, line))

    tokens.append(Token("EOF", "", line))
    return tokens
