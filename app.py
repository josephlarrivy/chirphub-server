from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Chirp


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///chirphub-db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "qwhdu&*UJdwqdqw"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/test', methods=['POST'])
def testing_api():
    data = request.get_json()
    response = User.test(data)
    return response

@app.route('/register', methods=['POST'])
def register_new_user():
    data = request.get_json()
    username = data.get('username')
    displayname = data.get('displayname')
    avatarColor = data.get('avatarColor')
    password = data.get('password')
    token_bytes = User.register(username, displayname, avatarColor, password)
    token_string = token_bytes.decode('utf-8')
    return jsonify({'token': token_string})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    token_bytes = User.authenticate(username, password)
    token_string = token_bytes.decode('utf-8')
    return jsonify({'token': token_string})

@app.route('/postChirp', methods=['POST'])
def post_chirp():
    data = request.get_json()
    user_id = data.get('user_id')
    timestamp = data.get('timestamp')
    text = data.get('text')
    image = data.get('image')
    response = Chirp.post_chirp(user_id, timestamp, text, image)
    return jsonify({'chirp_id': response})


@app.route('/addTag', methods=['POST'])
def add_tag():
    data = request.get_json()
    chirp_id = data.get(chirp_id)
    tag_name = data.get(tag_name)

    print(chirp_id, tag_name)

    # response = Chirp.post_chirp(user_id, timestamp, text, image)
    return jsonify({'status': 'testing'})






if __name__ == '__main__':
    app.run(debug=True)