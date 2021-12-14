from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from queue import Queue
import random


codes = {}
redirect_url = 'https://braden-discord-bot.herokuapp.com/'
os.environ['FLASK_APP'] = 'api.py'

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def redirect(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        code = request.args.get('code')
        key = random.getrandbits(128)
        final_url = f'{redirect_url}?code={code}'
        codes[key] = final_url
        return f"Key: {str(key)}"
        
    elif request.method == 'POST':
        print("POST")
        # code = request.args.get('code')
        # codes.put(f'{redirect_url}?code={code}')
        # return f'<h1>POST:{code}</h1>'


@app.route('/token/', methods=['GET'])
def get_token(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        key = request.args.get('key')
        if key is None:
            return "<h1>Are you lost?</h1>"
        if key not in codes:
            return "<h1>Stop in the name of love</h1>"
        url = codes[key]  
        del codes[key]
        print(123, url)
        return url



PORT = int(os.getenv("PORT", 8080))
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))
# app.run(host="0.0.0.0", debug=DEBUG_MODE, port=PORT)