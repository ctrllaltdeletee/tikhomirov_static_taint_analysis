from flask import Flask, request
import pickle
import base64

app = Flask(__name__)

@app.route('/pickle_unsafe')
def pickle_unsafe():
    data = request.args.get('data')
    obj = pickle.loads(base64.b64decode(data))
    return str(obj)
