from flask import Flask, request
import os

app = Flask(__name__)

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

@app.route('/path_traversal')
def path_traversal():
    param = request.args.get('file')
    return read_file(param)