import yaml
from flask import Flask, request

app = Flask(__name__)

@app.route('/yaml_unsafe')
def yaml_unsafe():
    data = request.args.get('data')
    obj = yaml.load(data, Loader=yaml.Loader)
    return str(obj)