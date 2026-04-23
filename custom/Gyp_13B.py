from flask import Flask, request
import subprocess

app = Flask(__name__)

class Safe:
    def execute(self, cmd):
        return "safe"

class Unsafe:
    def execute(self, cmd):
        subprocess.run(cmd, shell=True)

@app.route('/dynamic_typing_dict')
def dynamic_typing_dict():
    t = request.args.get('type')
    cmd = request.args.get('cmd')
    handlers = {
        'safe': Safe(),
        'unsafe': Unsafe()
    }
    obj = handlers.get(t, Safe())
    obj.execute(cmd)
    return "done"
