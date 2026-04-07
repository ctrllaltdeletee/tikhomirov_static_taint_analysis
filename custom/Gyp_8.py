from flask import Flask, request
import helpers.separate_request
import helpers.db_sqlite

app = Flask(__name__)

def id1(x):
    return x

def id2(x):
    return id1(x)

def id3(x):
    return id2(x)

@app.route('/sqli_chain')
def sqli_chain():
    wrapped = helpers.separate_request.request_wrapper(request)
    param = wrapped.get_form_parameter("test")
    bar = id3(param)
    sql = f"SELECT * FROM users WHERE name = '{bar}'"
    conn = helpers.db_sqlite.get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    return "done"