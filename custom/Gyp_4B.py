from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/sanitized_sql')
def sanitized_sql():
    raw = request.args.get('id')
    safe_int = int(raw)
    conn = sqlite3.connect('test.db')
    query = "SELECT * FROM users WHERE id = " + str(safe_int)
    conn.execute(query)
    return "ok"
