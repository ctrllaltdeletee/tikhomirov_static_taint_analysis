from flask import Flask, request
import os

app = Flask(__name__)

class UnsafeHandler:
    def execute(self, cmd):
        os.system(cmd)
class SafeHandler:
    def execute(self, cmd):
        print(f"Would execute: {cmd}")

def get_handler(flag):
    if flag:
        return UnsafeHandler()
    else:
        return SafeHandler()

@app.route('/cmd_isinstance')
def cmd_isinstance():
    cmd = request.args.get('cmd', '')
    flag = request.args.get('flag', 'false') == 'true'
    
    handler = get_handler(flag)
    
    if isinstance(handler, UnsafeHandler):
        handler.execute(cmd)
    else:
        return "Safe mode"
    
    return "Executed"
