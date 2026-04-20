from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/cmd_os')
def cmd_os():
    param = request.args.get('cmd')
    os.system(param)
    return "done"
