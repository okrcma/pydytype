import inspect
import os
import runpy
import sys
import threading

from parse import ModuleTypes

dirname = os.path.dirname(os.path.abspath(__file__))


def analyze_signle_module(full_path):
    def frame_callback(frame, event, arg):
        frameinfo = inspect.getframeinfo(frame)
        if frameinfo.filename != full_path:
            return frame_callback

        for varname, varvalue in frame.f_locals.items():
            vartype_str = types.get_type_str(frameinfo.lineno, varname)
            if vartype_str is not None:
                vartype = eval(vartype_str, frame.f_globals, frame.f_locals)
            else:
                vartype = None

            print("line number:", frameinfo.lineno)
            print("varname:    ", varname)
            print("varvalue:   ", varvalue)
            print("vartype_str:", vartype_str)
            print("vartype:    ", vartype)
            print()

        return frame_callback

    types = ModuleTypes.parse_module(full_path)

    threading.settrace(frame_callback)
    sys.settrace(frame_callback)

    runpy.run_path(full_path, run_name="__main__")


if __name__ == "__main__":
    print("hello")
    analyze_signle_module(dirname + "/example/example.py")
