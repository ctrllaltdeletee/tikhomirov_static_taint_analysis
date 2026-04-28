from flask import Flask, request
import sqlite3
from helpers import id3

app = Flask(__name__)

@app.route('/sqli_identity')
def sqli_identity():
    param = request.args.get('name', '')
    bar = id3(param)
    sql = f"SELECT * FROM users WHERE name = '{bar}'"
    conn = sqlite3.connect('example.db')
    conn.execute(sql)
    return "done"
