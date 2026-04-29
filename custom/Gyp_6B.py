from flask import Flask, request

app = Flask(__name__)

@app.route('/xss-keys', methods=['POST'])
def xss_keys():
    field_name = next(iter(request.form.keys()), "")
    return f"<div>{field_name}</div>"
