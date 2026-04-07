from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/xss_true')
def xss_true():
    data = request.args.get('data')
    template = f"<html><body>{data}</body></html>"
    return render_template_string(template)