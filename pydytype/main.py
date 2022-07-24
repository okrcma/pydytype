import os
import runpy

from pydytype.check import TraceTypeChecker

dirname = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    checker = TraceTypeChecker()
    checker.start_trace()
    runpy.run_path(dirname + "/../tests/examples/list.py", run_name="__main__")
    for result in checker.results:
        print(result)
