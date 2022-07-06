def example_builtins(a: int, b: str) -> None:
    return str(a) + str(b)


def example_list(a: list[int]):
    return a


if __name__ == "__main__":
    example_builtins("string", 42)
    example_list(5)
