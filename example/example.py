def example_unannotated(a, b):
    return a


def example_builtins(a: int, b: str) -> None:
    return str(a) + str(b)


def example_list(a: list[int]):
    return a


def example_nested_list(a: list[list[int]]):
    return a


def example_dict(b: dict[str, int]):
    return b


if __name__ == "__main__":
    example_unannotated(1, "b")
    example_builtins("string", 42)
    example_list(5)
    example_nested_list([[1, 2, 3]])
    example_dict({1: "a"})
