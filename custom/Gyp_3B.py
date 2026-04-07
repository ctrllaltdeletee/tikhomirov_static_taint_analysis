@app.route('/cmd_list')
def cmd_list():
    param = request.args.get('file')
    subprocess.run(['ls', param])