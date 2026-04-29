from flask import Flask, request

app = Flask(__name__)

storage = {}

@app.route('/store')
def store():
    storage['x'] = request.args.get('name', '')
    return "stored"

@app.route('/retrieve')
def retrieve():
    value = storage.get('x', '')
    return f"<h1>{value}</h1>"
