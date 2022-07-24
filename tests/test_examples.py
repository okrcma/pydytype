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
    runpy.run_path(path, run_name="__main__")
    checker.stop_trace()

    comments = parse_module_comments(path)

    for result in checker.results:
        if result.type_is_correct:
            continue
        comment = comments.get(result.line)
        if comment is None or parse_command_comment(comment) != "test_assert_fail":
            assert False, result
