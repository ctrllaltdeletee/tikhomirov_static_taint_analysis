from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/cmd_list')
def cmd_list():
    param = request.args.get('file')
    subprocess.run(['ls', param])
    return "done"
