from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route('/cmdi_chain')
def cmdi_chain():
    user_input = request.args.get('cmd', '')
    s = user_input
    if os.urandom(1)[0] > 128:
        s = s + 'a0'
    else:
        s = s + 'b0'
    if os.urandom(1)[0] > 128:
        s = s + 'a1'
    else:
        s = s + 'b1'
    if os.urandom(1)[0] > 128:
        s = s + 'a2'
    else:
        s = s + 'b2'
    if os.urandom(1)[0] > 128:
        s = s + 'a3'
    else:
        s = s + 'b3'
    if os.urandom(1)[0] > 128:
        s = s + 'a4'
    else:
        s = s + 'b4'
    subprocess.run(s, shell=True)
    return "done"
