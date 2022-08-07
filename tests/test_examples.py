import os
import runpy

import pytest

from pydytype.check import TraceTypeChecker
from pydytype.comments import parse_module_comments, parse_command_comment

_examples_dirpath = os.path.join(os.path.dirname(__file__), "examples")
_example_modules = [
    os.path.join(_examples_dirpath, filename)
    for filename in os.listdir(_examples_dirpath)
]


@pytest.mark.parametrize("path", _example_modules)
def test_module(path):
    checker = TraceTypeChecker(path_prefix=_examples_dirpath)
    checker.start_trace()
    try:
        runpy.run_path(path, run_name="__main__")
    except Exception as exc:
        checker.stop_trace()
        raise exc
    checker.stop_trace()

    checked_lines = set()
    comments = parse_module_comments(path)
    for result in checker.results:
        checked_lines.add(result.line)
        comment = comments.get(result.line)
        command = parse_command_comment(comment)
        if (command == "test_assert_fail") == result.type_is_correct:
            assert False, result

    for line, comment in comments.items():
        if line in checked_lines:
            continue
        command = parse_command_comment(comment)
        assert command != "test_assert_fail", f"No incorrect types on line {line}."
