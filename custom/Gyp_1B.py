from flask import Flask, request
import sqlite3
from helpers import my_propagator

app = Flask(__name__)

@app.route('/test')
def test():
    tainted = request.args.get('id', '')
    param = my_propagator(tainted)
    conn = sqlite3.connect(':memory:')
    conn.execute(f"SELECT * FROM users WHERE id = '{param}'")
    return "done"
