from flask import request
import yaml
from helper_module import OpaqueWrapper

def external_deserialization():
    param = request.headers.get("test")
    if not param:
        param = ""

    wrapper = OpaqueWrapper()
    bar = wrapper.do_something(param)

    yobj = yaml.load(bar, Loader=yaml.Loader)
    return yobj
