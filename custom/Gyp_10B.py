from flask import Flask, request

app = Flask(__name__)

@app.route('/exec_dynamic')
def exec_dynamic():
    data = request.args.get('func')
    exec(f"def dynamic(): return {data}")
    return "done"