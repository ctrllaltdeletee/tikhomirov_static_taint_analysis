from flask import Flask, request
import subprocess

app = Flask(__name__)

class Unsafe:
    def unsafe_exec(self, cmd):
        subprocess.run(cmd, shell=True)
    
    def safe_exec(self, cmd):
        return "safe"

@app.route('/test_dynamic_method')
def test_dynamic_method():
    cmd = request.args.get('cmd')
    method_name = request.args.get('method')
    handler = Unsafe()
    method = getattr(handler, method_name, None)
    if method:
        method(cmd)    
    return "done"
