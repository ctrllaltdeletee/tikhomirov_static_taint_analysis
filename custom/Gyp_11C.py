from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/list_index_dynamic')
def list_index_dynamic():
    idx = request.args.get('idx', '0')
    try:
        index = int(idx)
    except:
        index = 0
    commands = ['echo safe', 'rm -rf /']
    cmd = commands[index]
    os.system(cmd)
    return "Executed"