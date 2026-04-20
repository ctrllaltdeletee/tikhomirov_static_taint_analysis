@app.route('/list_flow')
def list_flow():
    idx = request.args.get('idx')
    user_cmd = request.args.get('cmd')
    cmds = ['echo hello', user_cmd] 
    try:
        index = int(idx)
    except:
        index = 0
    cmd = cmds[index] 
    os.system(cmd)
