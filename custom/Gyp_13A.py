from flask import Flask, request
import subprocess

app = Flask(__name__)

class Safe:
    def execute(self, cmd):
        return "safe"

class Unsafe:
    def execute(self, cmd):
        subprocess.run(cmd, shell=True)

def get_handler(flag):
    if flag == '1':
        return Safe()
    else:
        return Unsafe()

@app.route('/test')
def test():
    flag = request.args.get('flag')
    cmd = request.args.get('cmd')
    handler = get_handler(flag)
    handler.execute(cmd)
    return "done"