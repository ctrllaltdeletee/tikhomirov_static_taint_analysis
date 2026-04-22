from flask import Flask, request

app = Flask(__name__)

@app.route('/eval_obfuscated')
def eval_obfuscated():
    data = request.args.get('code')
    part1 = request.args.get('p1')
    part2 = request.args.get('p2')
    part3 = request.args.get('p3')
    part4 = request.args.get('p4')
    func_name = part1 + part2 + part3 + part4
    builtins_mod = __import__('builtins')
    unsafe_func = getattr(builtins_mod, func_name)
    unsafe_func(data)
    return "done"
