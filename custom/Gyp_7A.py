from flask import Flask, request
import yaml

app = Flask(__name__)

class OpaqueWrapper:
    def do_something(self, data):
        return data

@app.route('/inlined_insecure_deserialization')
def inlined_insecure_deserialization():
    param = request.headers.get("test")
    if not param:
        param = ""

    wrapper = OpaqueWrapper()
    bar = wrapper.do_something(param)

    yaml.load(bar, Loader=yaml.Loader)
    return "done"
