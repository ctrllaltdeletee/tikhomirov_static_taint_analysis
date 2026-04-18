from flask import Flask, request
import sqlite3

app = Flask(__name__)

def id1(x):
    return x

def id2(x):
    return id1(x)

def id3(x):
    return id2(x)

@app.route('/sqli_identity')
def sqli_identity():
    param = request.args.get('name', '')
    bar = id3(param)
    sql = f"SELECT * FROM users WHERE name = '{bar}'"
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    return "Done"