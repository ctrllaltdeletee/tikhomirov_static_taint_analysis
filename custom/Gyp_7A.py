from flask import request
import yaml

class OpaqueWrapper:
    def do_something(self, data):
        return data

def inlined_deserialization():
    param = request.headers.get("test")
    if not param:
        param = ""

    wrapper = OpaqueWrapper()
    bar = wrapper.do_something(param)

    yobj = yaml.load(bar, Loader=yaml.Loader)
    return yobj
