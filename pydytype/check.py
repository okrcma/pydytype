"""Module for checking types of variables at runtime."""

from __future__ import annotations

import inspect
import os
import sys
import threading
import types
import typing

from dataclasses import dataclass
from typing import Any

from pydytype.parse import parse_module


@dataclass
class Result:
    """Holds variable type check results."""

    module_path: str
    line: int
    varname: str
    varvalue: Any
    vartype_str: str
    vartype: Any
    type_is_correct: bool


class TypeCheckError(Exception):
    pass


class TraceTypeChecker:
    """Checks types while the program is running.

    The checker sets a tracing function and on each frame evaluates variable types.
        The results are saved to self.results.

    Since the checker uses tracing, debugging will not work while the checker is running.

    Attributes:
        path_prefix: Types will be checked only in modules with this prefix.
        results: List of type checking results.

    """

    def __init__(self, path_prefix: str = ""):
        """Initialize."""
        self.path_prefix = path_prefix

        self.results: list[Result] = []
        self._types: dict[str, list[dict[str, str]]] = {}

    def start_trace(self):
        """Start tracing."""
        threading.settrace(self._trace)
        sys.settrace(self._trace)

    def stop_trace(self):
        """Stop tracing."""
        threading.settrace(None)
        sys.settrace(None)

    def _trace(self, frame: types.FrameType, event: str, arg: Any):
        """Main trace method."""
        self._check_frame(frame)
        return self._trace

    def _check_frame(self, frame: types.FrameType):
        """Check frame for variable types and save the result."""
        frameinfo = inspect.getframeinfo(frame)
        if not frameinfo.filename.startswith(self.path_prefix) or not os.path.exists(
            frameinfo.filename
        ):
            return

        for varname, varvalue in frame.f_locals.items():
            vartype_str = self._get_type_str(
                frameinfo.filename, frameinfo.lineno, varname
            )
            if vartype_str is None:
                continue

            vartype = eval(vartype_str, frame.f_globals, frame.f_locals)
            type_is_correct = check_type(varvalue, vartype)

            result = Result(
                module_path=frameinfo.filename,
                line=frameinfo.lineno,
                varname=varname,
                varvalue=varvalue,
                vartype_str=vartype_str,
                vartype=vartype,
                type_is_correct=type_is_correct,
            )
            self.results.append(result)

    def _get_type_str(self, module_full_path: str, line: int, varname: str) -> str:
        """Get type string for a module name, line number and variable name."""
        if module_full_path not in self._types:
            module_types = parse_module(module_full_path)
            self._types[module_full_path] = module_types
        return self._types[module_full_path][line].get(varname)


def check_type(varvalue: Any, vartype: Any) -> bool:
    """Check whether the value fits the type."""
    origin = typing.get_origin(vartype)
    if origin is not None:
        if origin in _type_checker_map:
            return _type_checker_map[origin](varvalue, vartype)
        raise TypeCheckError(
            f"Didn't check type for varvalue: {varvalue}, vartype:{vartype}, "
            f"origin: {origin}."
        )
    return isinstance(varvalue, vartype)


def _check_type_list(varvalue, vartype):
    if not isinstance(varvalue, list):
        return False

    args = vartype.__args__
    if len(args) != 1:
        return False

    inner_type = args[0]
    for inner_value in varvalue:
        if not check_type(inner_value, inner_type):
            return False
    return True


def _check_type_set(varvalue, vartype):
    if not isinstance(varvalue, set):
        return False

    args = vartype.__args__
    if len(args) != 1:
        return False

    inner_type = args[0]
    for inner_value in varvalue:
        if not check_type(inner_value, inner_type):
            return False
    return True


def _check_type_dict(varvalue, vartype):
    if not isinstance(varvalue, dict):
        return False

    args = vartype.__args__
    if len(args) != 2:
        return False

    key_type, value_type = args
    for key_value, value_value in varvalue.items():
        if not check_type(key_value, key_type) or not check_type(
            value_value, value_type
        ):
            return False
    return True


_type_checker_map = {
    list: _check_type_list,
    set: _check_type_set,
    dict: _check_type_dict,
}

if __name__ == "__main__":
    import runpy
    import parse

    checker = TraceTypeChecker()
    checker.start_trace()
    runpy.run_path(parse.__file__, run_name="__main__")
    for result in checker.results:
        print(result)
