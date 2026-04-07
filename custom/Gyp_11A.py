from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/dict_flow')
def dict_flow():
    data = request.args.get('cmd')
    d = {}
    d['key'] = data
    cmd = d['key']
    os.system(cmd)