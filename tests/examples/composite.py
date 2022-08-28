def pass_list_set(a: list[set[int]]):
    return a


def fail_list_set(a: list[set[str]]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


def pass_list_dict_set(a: list[dict[int, set[str]]]):
    return a


def fail_list_dict_set(a: list[dict[int, set[str]]]):  # pydytype: test_assert_fail
    return a  # pydytype: test_assert_fail


if __name__ == "__main__":
    pass_list_set([])
    pass_list_set([set(), {1, 1}, {1, 2, 3}])

    fail_list_set([{"1", 2, "3"}])

    pass_list_dict_set([{1: {"a"}}])
    pass_list_dict_set([{1: set()}])
    pass_list_dict_set([{}])

    fail_list_dict_set([{1: {1}}])
