@app.route('/sanitized_sql')
def sanitized_sql():
    from flask import request
    raw = request.args.get('id')
    safe_int = int(raw)
    conn = sqlite3.connect('test.db')
    query = "SELECT * FROM users WHERE id = " + str(safe_int)
    conn.execute(query)
    return "ok"