from flask import Flask, request

app = Flask(__name__)

@app.route('/eval_reflect')
def eval_reflect():
    data = request.args.get('code')
    eval(data)
    return "done"