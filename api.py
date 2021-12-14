from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import asyncio


codes = asyncio.Queue()
redirect = 'https://braden-discord-bot.herokuapp.com/'
os.environ['FLASK_APP'] = 'api.py'

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def get_token(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        code = request.args.get('code')
        codes.put(f'{redirect}?code={code}')
        return f'<h1>GET:{code}</h1>'
    elif request.method == 'POST':
        print("POST")
        code = request.args.get('code')
        codes.put(f'{redirect}?code={code}')
        return f'<h1>POST:{code}</h1>'


@app.route('/token', methods=['GET'])
def get_token(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        code = codes.get()
        return f'{redirect}?code={code}'
    elif request.method == 'POST':
        print("POST")
        code = codes.get()
        return f'{redirect}?code={code}'



PORT = int(os.getenv("PORT", 8080))
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))
# app.run(host="0.0.0.0", debug=DEBUG_MODE, port=PORT)