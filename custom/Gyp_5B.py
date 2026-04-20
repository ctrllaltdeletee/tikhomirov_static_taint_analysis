from flask import Flask
import secrets

app = Flask(__name__)

@app.route('/strong_random')
def strong_random():
    token = secrets.randbelow(10**6)
    return str(token)
