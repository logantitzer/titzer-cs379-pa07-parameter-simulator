"""
PA 4: The USILang Symbol Table -- starter.

Complete Environment and check_program below. See
PA_04_The_USILang_Symbol_Table.md, Part B, for the full requirements.
"""

from typing import Optional

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass


class Environment:
    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.parent = parent
        self._names: dict = {}  # name -> declaration line, THIS scope only

    def define(self, name: str, line: int) -> None:
        """
        Store name -> line in THIS scope. Raise SemanticError if `name`
        is already defined in THIS scope (not a parent scope --
        shadowing a parent name is allowed).
        """
        if name in self._names:
            raise SemanticError(
                f"Duplicate declaration of {name!r} "
                f"(line {line}; originally declared line {self._names[name]})."
            )
        self._names[name] = line

    def resolve(self, name: str, line: Optional[int] = None) -> int:
        """
        Look up `name` in this scope, then climb `parent` links.
        Return the declaration line, or raise SemanticError if not
        found anywhere in the chain.

        `line` (optional) is the line of the offending reference; it is
        only used to build the error message.
        """
        env: Optional[Environment] = self
        while env is not None:
            if name in env._names:
                return env._names[name]
            env = env.parent
        where = f" (line {line})" if line is not None else ""
        raise SemanticError(f"Use of undeclared variable {name!r}{where}.")


def _check_expr(node, env: Environment) -> None:
    """Recursively resolve every Variable reference inside an expression."""
    if isinstance(node, Number):
        return
    if isinstance(node, Variable):
        env.resolve(node.name, node.line)
    elif isinstance(node, BinOp):
        _check_expr(node.left, env)
        _check_expr(node.right, env)
    else:
        raise TypeError(f"Unknown expression node: {node!r}")


def check_program(ast: Program) -> Environment:
    """
    Walk `ast.statements` in order, using one top-level Environment.

    For a Declaration: resolve every Variable in its expr BEFORE
    defining the new name (so `let x = x;` fails as use-before-decl).
    For an Assignment: resolve the assigned-to name, then resolve
    every Variable in its expr. Errors must surface at the first
    offending statement, not be collected and reported together.
    """
    env = Environment()  # top-level scope, parent=None
    for stmt in ast.statements:
        if isinstance(stmt, Declaration):
            _check_expr(stmt.expr, env)          # RHS first ...
            env.define(stmt.name, stmt.line)     # ... then bind the new name
        elif isinstance(stmt, Assignment):
            env.resolve(stmt.name, stmt.line)    # target must already exist
            _check_expr(stmt.expr, env)
        else:
            raise TypeError(f"Unknown statement node: {stmt!r}")
    return env