from lxml import etree
from flask import Flask, request

app = Flask(__name__)

@app.route('/xpath')
def xpath():
    user_input = request.args.get('name')
    xml = "<root><name>Alice</name></root>"
    tree = etree.XML(xml)
    query = f"//name[text()='{user_input}']"
    result = tree.xpath(query)
    return str(result)