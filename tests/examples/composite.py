def pass_list_dict(a: list[set[int]]):
    return a


def fail_list_dict(a: list[set[str]]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


if __name__ == "__main__":
    pass_list_dict([])
    pass_list_dict([set(), {1, 1}, {1, 2, 3}])

    fail_list_dict([{"1", 2, "3"}])
