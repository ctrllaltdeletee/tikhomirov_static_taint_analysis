import sqlite3
from flask import Flask

app = Flask(__name__)

@app.route('/safe_sql')
def safe_sql():
    user_input = "1"
    conn = sqlite3.connect('test.db')
    query = "SELECT * FROM users WHERE id = " + user_input
    conn.execute(query)
    return "done"
