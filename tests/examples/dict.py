def pass_dict(a: dict[str, int]):
    return a


def fail_dict(a: dict[str, int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def pass_nested_dict(a: dict[str, dict[int, dict[int, int]]]):
    return a


def fail_nested_dict(a: dict[int, dict[int, int]]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def pass_no_args_dict(a: dict):
    return a


def fail_incorrect_args_dict(a: dict[str]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def fail_slice_args_dict(a: dict[int:int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


if __name__ == "__main__":
    pass_dict({})
    pass_dict({"a": 1})

    fail_dict({"a": "b"})
    fail_dict({1: 2})
    fail_dict({"a": 1, "b": "c"})

    pass_nested_dict({"a": {}, "b": {1: {1: 2}, 2: {}}})

    fail_nested_dict({1: {1: "a"}})

    pass_no_args_dict({})
    pass_no_args_dict({"a": "b", "c": "d"})
    pass_no_args_dict({1: "b", "c": 2})

    fail_incorrect_args_dict({"a": "b"})

    fail_slice_args_dict({1: 2})
