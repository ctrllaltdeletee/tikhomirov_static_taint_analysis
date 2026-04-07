import os

@app.route('/cmd_os')
def cmd_os():
    param = request.args.get('cmd')
    os.system(param)