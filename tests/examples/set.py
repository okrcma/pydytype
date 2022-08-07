def pass_set(a: set[str]):
    return a


def fail_set(a: set[int]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


if __name__ == "__main__":
    pass_set({"a", "b", "a"})

    fail_set(1)
    fail_set({1, "a", 1})
