from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Chirp, Tag, ChirpTag


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///chirphub-db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "qwhdu&*UJdwqdqw"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# toolbar = DebugToolbarExtension(app)


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
    chirp_id = data.get('chirp_id')
    tag_name = data.get('tag_name')

    tag_id = Tag.create_tag(tag_name)
    print(tag_id)

    join = ChirpTag.connect_tag_to_chirp(chirp_id, tag_id)
    print(join)
        
    return jsonify({'status': 'testing'})

@app.route('/getChirps', methods=['GET'])
def get_chirps():
    chirps = Chirp.query.all()
    chirps_data = []

    for chirp in reversed(chirps):
        chirp_data = {
            "id": chirp.id,
            "username": chirp.user.username,
            "displayName": chirp.user.displayname,
            "avatar": chirp.user.avatar,
            "timestamp": chirp.timestamp.isoformat(),
            "text": chirp.text,
            "image": chirp.image,
            "likes": len(chirp.likes),
            "rechirps": chirp.rechirps,
            "comments": chirp.comments
        }
        chirps_data.append(chirp_data)

    return jsonify({'data' : chirps_data})

@app.route('/likeChirp/<chirp_id>/<user_id>', methods=['POST'])
def like_chirp(chirp_id, user_id):
    chirp = Chirp.query.get(chirp_id)
    if chirp is None:
        return jsonify({'message': 'Chirp not found'}), 404

    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    like = chirp.add_like(user_id)

    return jsonify({'message': 'Chirp liked successfully'})

@app.route('/deleteChirp/<chirp_id>', methods=['POST'])
def delete_chirp(chirp_id):
    chirp = Chirp.query.get(chirp_id)
    if chirp is None:
        return jsonify({'message': 'Chirp not found'}), 404

    db.session.delete(chirp)
    db.session.commit()

    return jsonify({'message': 'Chirp deleted successfully'})




if __name__ == '__main__':
    app.run(debug=True)