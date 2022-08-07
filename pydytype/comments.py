"""Module for parsing comments from module source code."""

from __future__ import annotations

import re
import tokenize


def parse_module_comments(filename: str) -> dict[int, str]:
    """Parse module code to get comments (starting with #) on each line."""
    comments = {}
    with open(filename, "rb") as f:
        for toktype, tokstring, (line, _), _, _ in tokenize.tokenize(f.readline):
            if toktype == tokenize.COMMENT:
                comments[line] = tokstring
    return comments


def parse_command_comment(comment: str | None) -> str | None:
    """Parse comment string to see if it's a pydytype command and return the command."""
    if comment is None:
        return None

    pattern = "^#\\s*pydytype:\\s*(.+)$"
    match = re.match(pattern, comment)
    if match is not None:
        return match.group(1)


if __name__ == "__main__":
    # some comment
    comments = parse_module_comments(__file__)  # another comment
    print(comments)
