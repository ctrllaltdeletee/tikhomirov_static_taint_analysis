import random
from flask import Flask

app = Flask(__name__)

@app.route('/weak_random')
def weak_random():
    token = random.randrange(10**6)
    return str(token)