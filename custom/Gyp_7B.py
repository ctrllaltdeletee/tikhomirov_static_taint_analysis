from flask import Flask, request
import yaml
from helpers import OpaqueWrapper

app = Flask(__name__)

@app.route('/external_deserialization')
def external_deserialization():
    param = request.headers.get("test")
    if not param:
        param = ""

    wrapper = OpaqueWrapper()
    bar = wrapper.do_something(param)

    yaml.load(bar, Loader=yaml.Loader)
    return "done"
