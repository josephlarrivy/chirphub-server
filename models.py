from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import uuid
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from datetime import datetime, timedelta
import base64
import json
import random
import string

secret_key = 'qwhdu&*UJdwqdqw'

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

def generate_random_string(length=30):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string





###########################################################


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    displayname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(300), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    bookmarks = db.relationship('Bookmark', back_populates='user')

    def __init__(self, username, displayname, avatar, password):
        self.id = 'user-' + str(uuid.uuid4())[:30]
        self.username = username
        self.displayname = displayname
        self.avatar = avatar
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def generate_token(self):
        payload = {
            'user_id': self.id,
            'username': self.username,
            'avatar': self.avatar,
            'displayname': self.displayname,
            'authenticated' : True
        }
        encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode())
        return encoded_payload

    @classmethod
    def test(cls, data):
        test_user = User(username='test_username', displayname='test_display_name', avatar='no_avatar', password='test_password')
        return test_user.generate_token()

    @classmethod
    def register(cls, username, displayname, avatar, password):
        user = cls(username, displayname, avatar, password)
        db.session.add(user)
        db.session.commit()
        return user.generate_token()

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user.generate_token()
        else:
            return None

    @classmethod
    def delete_user(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            db.session.delete(user)
            db.session.commit()
            return True
        else:
            return False


class Chirp(db.Model):
    __tablename__ = 'chirps'

    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    text = db.Column(db.String(290), nullable=False)
    image = db.Column(db.String(290), nullable=False)
    rechirps = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('User', backref='chirps')
    tags = db.relationship('Tag', secondary='chirps_tags', backref='chirps')
    likes = db.relationship('Like', backref='chirp')
    comments = db.relationship('Comment', backref='chirp_comments', cascade='delete, delete-orphan')
    bookmarks = db.relationship('Bookmark', back_populates='chirp')

    def __init__(self, user_id, timestamp, text, image):
        self.id = 'chirp-' + str(uuid.uuid4())[:30]
        self.user_id = user_id
        self.timestamp = timestamp
        self.text = text
        self.image = image

    @classmethod
    def post_chirp(cls, user_id, timestamp, text, image):
        chirp = Chirp(user_id=user_id, timestamp=timestamp, text=text, image=image)
        db.session.add(chirp)
        db.session.commit()
        return chirp.id

    def add_like(self, user_id):
        like = Like.add_like(chirp_id=self.id, user_id=user_id)
        return like

    @classmethod
    def get_tags_by_chirp_id(cls, chirp_id):
        chirp = cls.query.get(chirp_id)
        if chirp:
            tags_data = [{"tag_id": tag.id, "tag_name": tag.name} for tag in chirp.tags]
            return tags_data
        else:
            return "[]"

    @classmethod
    def get_chirps_by_tag_id(cls, tag_id):
        chirps = cls.query.filter(cls.tags.any(id=tag_id)).all()
        chirps_to_return = []
        for chirp in chirps:
            chirps_to_return.append({
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
        })
        return chirps_to_return

    @classmethod
    def delete_chirp(cls, chirp_id):
        chirp = cls.query.get(chirp_id)
        if chirp:
            try:
                ChirpTag.query.filter_by(chirp_id=chirp_id).delete()
                Like.query.filter_by(chirp_id=chirp_id).delete()
                Comment.query.filter_by(chirp_id=chirp_id).delete()
                Bookmark.query.filter_by(chirp_id=chirp_id).delete()

                db.session.delete(chirp)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return False
            return True
        else:
            return False



class ChirpTag(db.Model):
    __tablename__ = 'chirps_tags'

    chirp_id = db.Column(db.String(36), db.ForeignKey('chirps.id'), primary_key=True)
    tag_id = db.Column(db.String(36), db.ForeignKey('tags.id'), primary_key=True)

    chirp = db.relationship('Chirp', backref='chirp_tags', cascade="delete")
    tag = db.relationship('Tag', backref='chirp_tags')

    @classmethod
    def connect_tag_to_chirp(cls, chirp_id, tag_id):
        chirp_tag = cls(chirp_id=chirp_id, tag_id=tag_id)
        db.session.add(chirp_tag)
        db.session.commit()
        return chirp_tag


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.id = 'tag-' + str(uuid.uuid4())[:30]
        self.name = name

    @classmethod
    def create_tag(cls, name):
        existing_tag = cls.query.filter_by(name=name).first()
        if existing_tag:
            return existing_tag.id
        else:
            tag = cls(name=name)
            db.session.add(tag)
            db.session.commit()
            return tag.id

    @classmethod
    def get_tag_by_name(cls, name):
        return cls.query.filter(cls.name.ilike(name)).first()

    @classmethod
    def get_all_tags(cls):
        return cls.query.all()

    @classmethod
    def delete_tag(cls, tag_id):
        tag = cls.query.get(tag_id)
        if tag:
            db.session.delete(tag)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def all_tags_except_one(cls, tag_id):
        tags = cls.query.filter(Tag.id != tag_id).all()
        tags_to_return = []
        for tag in tags:
            tags_to_return.append({'tagId':tag.id, 'tagName':tag.name})
        return tags_to_return

    @classmethod
    def get_all_tags_as_ojects(cls):
        tags = cls.query.order_by(cls.name).all()
        tags_to_return = []
        for tag in tags:
            tags_to_return.append({'tagId':tag.id, 'tagName':tag.name})
        return tags_to_return



class Like(db.Model):
    __tablename__ = 'chirp_likes'

    id = db.Column(db.Integer, primary_key=True)
    chirp_id = db.Column(db.String(36), db.ForeignKey('chirps.id'), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, chirp_id, user_id):
        self.chirp_id = chirp_id
        self.user_id = user_id

    @classmethod
    def add_like(cls, chirp_id, user_id):
        existing_like = cls.query.filter_by(chirp_id=chirp_id, user_id=user_id).first()
        if existing_like:
            return existing_like, False 

        like = cls(chirp_id=chirp_id, user_id=user_id)
        db.session.add(like)
        db.session.commit()
        return like, True



class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    text = db.Column(db.String(290), nullable=False)
    chirp_id = db.Column(db.String(36), db.ForeignKey('chirps.id'), nullable=False)

    user = db.relationship('User', backref='comments')
    chirp = db.relationship('Chirp', backref='comment')

    def __init__(self, user_id, timestamp, text, chirp_id):
        self.id = 'comment-' + str(uuid.uuid4())[:30]
        self.user_id = user_id
        self.timestamp = timestamp
        self.text = text
        self.chirp_id = chirp_id

    @classmethod
    def post_chirp_comment(cls, user_id, timestamp, text, chirp_id):
        comment = Comment(user_id=user_id, timestamp=timestamp, text=text, chirp_id=chirp_id)
        db.session.add(comment)
        db.session.commit()
        return comment.id

    @classmethod
    def delete_comment(cls, comment_id):
        comment = cls.query.get(comment_id)
        if comment:
            try:
                db.session.delete(comment)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return False
            return True
        else:
            return False



class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    def __init__(self, user_id, chirp_id):
        self.user_id = user_id
        self.chirp_id = chirp_id

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    chirp_id = db.Column(db.String(36), db.ForeignKey('chirps.id'))

    user = db.relationship('User', back_populates='bookmarks')
    chirp = db.relationship('Chirp', back_populates='bookmarks')

    @classmethod
    def add_bookmark(cls, user_id, chirp_id):
        bookmark = Bookmark(user_id, chirp_id)
        db.session.add(bookmark)
        db.session.commit()
        return bookmark.id

    @classmethod
    def get_bookmarks_by_user(cls, user_id):
        bookmarks = cls.query.filter_by(user_id=user_id).all()
        return bookmarks

    @classmethod
    def delete_bookmark(cls, user_id, chirp_id):
        bookmark = cls.query.filter_by(user_id=user_id, chirp_id=chirp_id).first()
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
            return True
        else:
            return False