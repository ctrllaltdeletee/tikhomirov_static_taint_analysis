from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/xss_false')
def xss_false():
    data = request.args.get('data')
    return jsonify({"data": data})