from flask import Flask
from flask_cors import CORS
import os



os.environ['FLASK_APP'] = 'api.py'

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"



PORT = int(os.getenv("PORT", 8080))
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))
app.run(host="0.0.0.0", debug=DEBUG_MODE, port=PORT)