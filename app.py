import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Chirp, Tag, ChirpTag, Comment, Like, Bookmark
# from itsdangerous import TimedJSONWebSignatureSerializer
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
CORS(app)
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://lqcsyelchadpfh:09adcf69af5a2bedecea33c10504fddc608b506fcc76b67ee6dd0672b74333f0@ec2-34-197-91-131.compute-1.amazonaws.com:5432/df4c5lrgso4jrp"


# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///chirphub-db"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', "postgresql:///chirphub-data")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "qwhdu&*UJdwqdqw"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)


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

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username taken'}), 409
    
    token_bytes = User.register(username, displayname, avatarColor, password)
    token_string = token_bytes.decode('utf-8')
    return jsonify({'token': token_string}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    token_bytes = User.authenticate(username, password)
    if token_bytes is None:
        return jsonify({'error': 'Invalid username or password'}), 401

    token_string = token_bytes.decode('utf-8')
    return jsonify({'token': token_string}), 200

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
            "comments": len(chirp.comments)
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
    success = Chirp.delete_chirp(chirp_id)
    if success:
        return jsonify(message="Chirp deleted successfully"), 202
    else:
        return jsonify(message="Chirp not found or failed to delete"), 204

@app.route('/postChirpComment', methods=['POST'])
def post_chirp_comment():
    data = request.get_json()

    user_id = data.get('user_id')
    timestamp = data.get('timestamp')
    text = data.get('text')
    chirp_id = data.get('chirp_id')

    print((user_id, timestamp, text, chirp_id))

    response = Comment.post_chirp_comment(user_id, timestamp, text, chirp_id)
    return jsonify({'chirp_id': response})

@app.route('/getCommentsByChirpId/<chirp_id>', methods=['POST'])
def get_comments_by_chirp_id(chirp_id):
    comments = Comment.query.filter_by(chirp_id=chirp_id).order_by(Comment.timestamp).all()

    comments_data = []

    for comment in reversed(comments):
        comment_data = {
            "username": comment.user.username,
            "displayName": comment.user.displayname,
            "avatar": comment.user.avatar,
            "timestamp": comment.timestamp.isoformat(),
            "text": comment.text,
            "id": comment.id
        }
        comments_data.append(comment_data)

    return jsonify({'data': comments_data})

@app.route('/getTagsByChirpId/<chirp_id>', methods=['POST'])
def get_tags_by_chirp_id(chirp_id):
    tags = Chirp.get_tags_by_chirp_id(chirp_id)

    return jsonify({'data': tags})

@app.route('/getChirpsByTagId/<tag_id>', methods=['POST'])
def get_chirps_by_tag_id(tag_id):
    chirps = Chirp.get_chirps_by_tag_id(tag_id)

    return jsonify({'data': chirps})

@app.route('/getAllTagsButCurrent/<tag_id>', methods=['POST'])
def get_all_tags_but_current(tag_id):
    tags = Tag.all_tags_except_one(tag_id)

    return jsonify({'data': tags})

@app.route('/getAllTagsAsObjects', methods=['GET'])
def get_all_tags_as_ojects():
    tags = Tag.get_all_tags_as_ojects()

    return jsonify({'data': tags})

@app.route('/addBookmark', methods=['POST'])
def add_bookmark():
    data = request.get_json()

    user_id = data.get('user_id')
    chirp_id = data.get('chirp_id')

    response = Bookmark.add_bookmark(user_id, chirp_id)
    return jsonify({'data': response})

@app.route('/getBookmarkedChirpsByUser', methods=['POST'])
def get_bookmarked_chirps():
    data = request.get_json()
    user_id = data.get('user_id')
    # print(user_id)
    
    bookmarks = Bookmark.get_bookmarks_by_user(user_id)
    chirp_ids = [bookmark.chirp_id for bookmark in bookmarks]
    
    chirps = Chirp.query.filter(Chirp.id.in_(chirp_ids)).all()
    # print(chirps)

    chirps_data = []
    for chirp in reversed(chirps):
        chirp_data = {
            'id': chirp.id,
            'username': chirp.user.username,
            'displayName': chirp.user.displayname,
            'avatar': chirp.user.avatar,
            'timestamp': chirp.timestamp.isoformat(),
            'text': chirp.text,
            'image': chirp.image,
            'likes': len(chirp.likes),
            'rechirps': chirp.rechirps,
            'comments': len(chirp.comments)
        }
        chirps_data.append(chirp_data)

    return jsonify({'data': chirps_data})

@app.route('/removeBookmark', methods=['POST'])
def remove_bookmark():
    data = request.get_json()

    user_id = data.get('user_id')
    chirp_id = data.get('chirp_id')

    response = Bookmark.delete_bookmark(user_id, chirp_id)
    return jsonify({'data': response})

@app.route('/deleteComment/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    success = Comment.delete_comment(comment_id)
    if success:
        return jsonify(message="Comment deleted successfully"), 202
    else:
        return jsonify(message="Comment not found or failed to delete"), 204



if __name__ == '__main__':
    app.run(debug=True)