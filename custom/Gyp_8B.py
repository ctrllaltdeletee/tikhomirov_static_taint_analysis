from flask import Flask, request
import sqlite3
from helpers import id3

app = Flask(__name__)

@app.route('/external_sqli_id')
def external_sqli_id():
    param = request.args.get('name', '')
    bar = id3(param)
    sql = f"SELECT * FROM users WHERE name = '{bar}'"
    conn = sqlite3.connect('example.db')
    conn.execute(sql)
    return "done"
