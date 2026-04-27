from flask import request
import yaml
import helper_module

def external_deserialization():
    param = request.headers.get("test")
    if not param:
        param = ""

    wrapper = helper_module.OpaqueWrapper()
    bar = wrapper.do_something(param)

    yobj = yaml.load(bar, Loader=yaml.Loader)
    return yobj
