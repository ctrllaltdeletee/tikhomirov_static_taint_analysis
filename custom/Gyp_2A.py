from flask import Flask, request, redirect

app = Flask(__name__)

def make_redirect(url):
    return redirect(url)

@app.route('/redirect')
def open_redirect():
    target = request.args.get('url')
    return make_redirect(target)