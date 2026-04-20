import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route('/cmd_conditional')
def cmd_conditional():
    param = request.args.get('cmd')
    bar = param
    if 'safe' in bar:
        bar = 'echo safe'
    subprocess.run(bar, shell=True)
    return "done"
