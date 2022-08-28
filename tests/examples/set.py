def pass_set(a: set[str]):
    return a


def fail_set(a: set[int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def pass_no_args_set(a: set):
    return a


def fail_incorrect_args_set(a: set[int, int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


if __name__ == "__main__":
    pass_set(set())
    pass_set({"a", "b", "a"})

    fail_set(1)
    fail_set({1, "a", 1})

    pass_no_args_set(set())
    pass_no_args_set({"a", "b", "a"})
    pass_no_args_set({1, 1})
    pass_no_args_set({1, "a"})

    fail_incorrect_args_set({1, 2})
