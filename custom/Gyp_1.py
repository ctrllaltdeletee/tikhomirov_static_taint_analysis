from flask import Flask, request
import helpers.separate_request
import helpers.db_sqlite

app = Flask(__name__)

@app.route('/sqli_wrapper', methods=['POST'])
def test_sqli_wrapper():
    wrapped = helpers.separate_request.request_wrapper(request)
    param = wrapped.get_form_parameter("test_param")
    if not param:
        param = ""
    bar = param
    sql = f"SELECT * FROM users WHERE name = '{bar}'"
    conn = helpers.db_sqlite.get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    return "done"