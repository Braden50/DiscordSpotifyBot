from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import os
from queue import Queue
import random
from bot import client

codes = {}
REDIRECT_URL = os.environ.get('SPOTIPY_REDIRECT_URI')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
if REDIRECT_URL is None:
    raise Exception("No spotify redirect uri provided")
if DISCORD_TOKEN is None:
    raise Exception("No spotify redirect uri provided")



app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def redirect(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        code = request.args.get('code')
        key = random.getrandbits(128)
        final_url = f'{REDIRECT_URL}?code={code}'
        codes[key] = final_url
        return f"Key: {str(key)}"
        
    elif request.method == 'POST':
        print("POST")


@app.route('/token/', methods=['GET'])
def get_token(): # this method gets all users
    if request.method == 'GET':
        print("GET")
        key = request.args.get('key')
        if key is None:
            return "<h1>Are you lost?</h1>"
        key = int(key)
        if key not in codes:
            "<h2>Invalid Key Provided</h2>"
            # return f"<h1>{key}</h1>\n<h3>{codes}</h3>"
        url = codes[key]  
        del codes[key]
        print(123, url)
        return url


print('Starting bot')
client.run(DISCORD_TOKEN)
print('Quit')

# bot.loop.create_task(audio_player_task())
# bot.run(DISCORD_TOKEN)

# PORT = int(os.getenv("PORT", 8080))
# DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))
# app.run(host="0.0.0.0", debug=DEBUG_MODE, port=PORT)