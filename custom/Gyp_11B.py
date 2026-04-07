from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/dict_key_dynamic')
def dict_key_dynamic():
    key = request.args.get('key', '')
    commands = {
        'safe': 'echo hello',
        'danger': 'rm -rf /'
    }
    cmd = commands.get(key, 'echo default')
    os.system(cmd)
    return "Executed"