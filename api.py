from flask import Flask
from flask_cors import CORS
import os



os.environ['FLASK_APP'] = 'api.py'

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def get_token(): # this method gets all users
    if request.method == 'GET':
        search_username = request.args.get('name')
        search_job = request.args.get('job')
        users = {}
        if search_username:
            if search_job:
                users['users_list'] = userModel.find_by_name_and_job(search_username, search_job)
                return users
            users['users_list'] = userModel.find_by_name(search_username)
            return users
        users['users_list'] = userModel.find_all()
        return users
    elif request.method == 'POST':
        userToAdd = request.get_json()
        newUser = User(userToAdd)
        newUser.save()
        resp = jsonify(newUser), 201
        # resp.status_code = 200 #optionally, you can always set a response code.
        # 200 is the default code for a normal response
        return resp



PORT = int(os.getenv("PORT", 8080))
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))
# app.run(host="0.0.0.0", debug=DEBUG_MODE, port=PORT)