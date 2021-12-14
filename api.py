from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from queue import Queue


codes = Queue(maxsize=10)
redirect_url = 'https://braden-discord-bot.herokuapp.com/'
os.environ['FLASK_APP'] = 'api.py'

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def redirect(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        code = request.args.get('code')
        codes.put(f'{redirect_url}?code={code}')
        return f'<h1>GET:{code}</h1>'
    elif request.method == 'POST':
        print("POST")
        code = request.args.get('code')
        codes.put(f'{redirect_url}?code={code}')
        return f'<h1>POST:{code}</h1>'


@app.route('/token/', methods=['GET'])
def get_token(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        url = codes.get()
        return url
    elif request.method == 'POST':
        print("POST")
        url = codes.get()
        return url



PORT = int(os.getenv("PORT", 8080))
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))
# app.run(host="0.0.0.0", debug=DEBUG_MODE, port=PORT)