def pass_list(a: list[str]):
    return a


def fail_list(a: list[int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def pass_nested_list(a: list[list[list[float]]]):
    return a


def fail_nested_list(a: list[list[int]]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def pass_no_args_list(a: list):
    return a


def fail_incorrect_args_list(a: list[int, int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


if __name__ == "__main__":
    pass_list([])
    pass_list(["txt"])

    fail_list(1)
    fail_list([1, 2, "3", 4])

    pass_nested_list([[[1.1, 5.2], []], []])

    fail_nested_list([1])

    pass_no_args_list([])
    pass_no_args_list(["a", "b"])
    pass_no_args_list([1])
    pass_no_args_list([1, "a"])

    fail_incorrect_args_list([1, 1])
