"""Module for parsing type annotations from a module source code."""

from __future__ import annotations
import ast
from typing import Callable, Any, Optional


# TODO returns, classes, for block, ...


def parse_module(filename: str) -> list[dict[str, str]]:
    """Parse module code and get variable type annotations for each line.

    Args:
        filename: Path to the module.

    Returns:
        Type annotations for each line.

    """
    types_store = ModuleTypesIntermediateStore()
    parser = ModuleTypesParser(types_store)
    parser.parse(filename)
    return types_store.get_types_by_line()


class ModuleTypesParser(ast.NodeVisitor):
    """Parses type annotations from module source code.

    Each visit_* method must return call either generic_visit or generic_leave method
        to ensure the leave methods are called properly. Method generic_visit should
        be called if inner nodes should be visited, and method generic_leave should
        be called if inner nodes should be skipped.

    """

    def __init__(self, types_store: ModuleTypesIntermediateStore):
        """Initialize the parser.

        Args:
            types_store: Storage for intermediate parsed type annotation results.

        """
        self.types_store = types_store

    def parse(self, filename: str):
        """Parse type annotations from a module.

        Stores intermediate results in self.types_store.

        Args:
            filename: Filepath of the module

        """
        with open(filename, "r") as f:
            source = f.read()

        node = ast.parse(source, filename)
        line_end = len(source.splitlines())
        self.types_store.start_scope(line_start=1, line_end=line_end)
        self.visit(node)
        self.types_store.end_scope()

    def leave(self, node: ast.AST):
        """Called at the end of each node visit."""
        method = "leave_" + node.__class__.__name__
        leaver: Callable[[ast.AST], Any] = getattr(self, method, self.generic_leave)
        return leaver(node)

    def generic_visit(self, node: ast.AST):
        """Called if no explicit visitor function exists for a node.

        Can also be called by an explicit visitor. Calls leave method.

        """
        tmp = super().generic_visit(node)
        self.leave(node)
        return tmp

    def generic_leave(self, node: ast.AST):
        """Called at the end of every node visit.

        Does not do anything. It is here just for completeness of the structure
            of methods.

        """
        pass

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit FunctionDef node."""
        self.types_store.start_scope(line_start=node.lineno, line_end=node.end_lineno)
        return self.generic_visit(node)

    def leave_FunctionDef(self, node: ast.FunctionDef):
        """Leave FunctionDef node."""
        self.types_store.end_scope()
        return self.generic_leave(node)

    def visit_arg(self, node: ast.arg):
        """Visit arg node."""
        self._handle_type(varname=node.arg, annotation=node.annotation)
        return self.generic_leave(node)

    def visit_Assign(self, node: ast.Assign):
        """Visit Assign node."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._handle_type(varname=target.id, annotation=None, line=node.lineno)
            # TODO other node types
        return self.generic_leave(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        """Visit AnnAssign node."""
        if isinstance(node.target, ast.Name):
            self._handle_type(
                varname=node.target.id, annotation=node.annotation, line=node.lineno
            )
        # TODO other node types
        return self.generic_leave(node)

    def visit_Global(self, node: ast.Global):
        """Visit Global node."""
        pass  # TODO

    def _handle_type(
        self, varname: str, annotation: Optional[ast.AST], line: Optional[int] = None
    ):
        """Store information about parsed type annotation.

        Args:
            varname: Name of variable.
            annotation: Type annotation of the variable as AST node, or None in case
                of assignment without annotation.
            line: First line number where the annotation takes effect, or None in case
                the annotation apply to the whole scope.

        """
        vartype = ast.unparse(annotation) if annotation is not None else None
        self.types_store.add_type(varname=varname, vartype=vartype, line=line)


class ModuleTypesIntermediateStore:
    """Stores type annotation information while it's being parsed.

    Methods start_scope, end_scope, add_type are used to store information about
        type annotations. Once all the information is stored, method get_types_by_line
        can be called to get the annotations in a line-by-line list.

    """

    class _Scope:
        """Container for variable type annotations within one scope."""

        def __init__(self, line_start: int, line_end: int):
            """Initialize the scope.

            Args:
                line_start: First line number of the scope.
                line_end: Last line number of the scope.

            """
            self.line_start: int = line_start
            self.line_end: int = line_end
            self._subscopes: list[ModuleTypesIntermediateStore._Scope] = []
            self._types_fifo: list[tuple[str, str, int, int]] = []

        def add_type(self, varname: str, vartype: str, line: int = None):
            """Add type annotation to the scope.

            Args:
                varname: Name of variable.
                vartype: Type annotation of the variable.
                line: First line number where the annotation takes effect.

            """
            line_start = line if line is not None else self.line_start
            self._types_fifo.append((varname, vartype, line_start, self.line_end))

        def add_subscope(self, subscope: ModuleTypesIntermediateStore._Scope):
            """Add subscope within this scope."""
            self._subscopes.append(subscope)

        def get_types_by_line_list(self) -> list[Optional[dict[str, str]]]:
            """Compile all the type annotations to a line-by-line list.

            Includes annotations from subscopes.

            """
            types_list = [None] * (self.line_end + 1)
            for line, data in self._get_types_by_line_dict().items():
                types_list[line] = data
            return types_list

        def _get_types_by_line_dict(self) -> dict[int, dict[str, str]]:
            """Compile all the type annotations to a line-by-line dict.

            Includes annotations from subscopes.

            """
            types = self._get_own_types()
            for subscope in self._subscopes:
                types = {**types, **subscope._get_types_by_line_dict()}
            return types

        def _get_own_types(self) -> dict[int, dict[str, str]]:
            """Compile all the type annotations to a line-by-line dict.

            Excludes annotations from subscopes.

            """
            types = {}
            for line in range(self.line_start, self.line_end + 1):
                types.setdefault(line, {})
            for varname, vartype, line_start, line_end in self._types_fifo:
                for line in range(line_start, line_end + 1):

                    if vartype is None:
                        types[line].setdefault(varname, vartype)
                    else:
                        types[line][varname] = vartype
            return types

    class _ScopeLinkedStack:
        """Stack of linked scopes."""

        def __init__(self):
            """Initialize empty stack."""
            self._stack: list[ModuleTypesIntermediateStore._Scope] = []

        def push(self, scope: ModuleTypesIntermediateStore._Scope):
            """Push new scope onto the stack and link it to the previous scope."""
            prev_scope = self.top()
            if prev_scope is not None:
                prev_scope.add_subscope(scope)
            self._stack.append(scope)

        def pop(self) -> ModuleTypesIntermediateStore._Scope:
            """Pop a scope from the stack, but don't unlink it from the next scope."""
            return self._stack.pop()

        def top(self) -> Optional[ModuleTypesIntermediateStore._Scope]:
            """Get the top scope without removing it from the stack."""
            if len(self._stack) == 0:
                return None
            return self._stack[-1]

    def __init__(self):
        """Initialize the store."""
        self._scope_stack = self._ScopeLinkedStack()
        self._bottom_scope = None

    def start_scope(self, line_start: int, line_end: int):
        """Start a new scope.

        Args:
            line_start: First line number of the scope.
            line_end: Last line number of the scope.

        """
        self._scope_stack.push(self._Scope(line_start, line_end))
        if self._bottom_scope is None:
            self._bottom_scope = self._scope_stack.top()

    def end_scope(self):
        """End current scope."""
        self._scope_stack.pop()

    def add_type(self, varname: str, vartype: str, line: int = None):
        """Add type annotation to current scope.

        Args:
            varname: Name of variable.
            vartype: Type annotation of the variable.
            line: First line number where the annotation takes effect.

        """
        self._scope_stack.top().add_type(varname, vartype, line)

    def get_types_by_line(self) -> list[dict[str, str]]:
        """Get type annotations line-by-line.

        The result is a list of dicts. Indices of the list are equal to line numbers,
        index 0 contains value None. The keys in the dicts are variable names, the
        values are type annotations as strings.

        Returns:
            Line-by-line type annotations.

        """
        return self._bottom_scope.get_types_by_line_list()


if __name__ == "__main__":
    types = parse_module(__file__)
    for line, type_dict in enumerate(types):
        print(line, type_dict)
