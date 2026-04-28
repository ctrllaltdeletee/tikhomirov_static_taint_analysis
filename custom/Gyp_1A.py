from flask import Flask, request
import sqlite3

app = Flask(__name__)

def my_propagator(value):
    return value

@app.route('/test')
def inlined_sqli():
    tainted = request.args.get('id', '')
    param = my_propagator(tainted)
    conn = sqlite3.connect(':memory:')
    conn.execute(f"SELECT * FROM users WHERE id = '{param}'")
    return "done"
