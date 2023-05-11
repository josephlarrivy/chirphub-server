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



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    displayname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(300), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

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
    likes = db.Column(db.Integer, nullable=False, default=0)
    rechirps = db.Column(db.Integer, nullable=False, default=0)
    comments = db.Column(db.Integer, nullable=False, default=0)

    tags = db.relationship('Tag', secondary='chirps_tags', backref='chirps')

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


class ChirpTag(db.Model):
    __tablename__ = 'chirps_tags'

    chirp_id = db.Column(db.String(36), db.ForeignKey('chirps.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

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

    # @classmethod
    # def create_tag(cls, name):
    #     tag = cls(name=name)
    #     db.session.add(tag)
    #     db.session.commit()
    #     return tag
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

    
    # @classmethod
    # def add_tag_to_chirp(cls, tag_name, chirp_id):
    #     tag = cls.get_tag_by_name(tag_name)
    #     if not tag:
    #         tag = cls.create_tag(tag_name)

    #     chirp = Chirp.query.get(chirp_id)
    #     print('111111111', tag.id)
    #     print('222222222', chirp_id)
    #     if chirp:
    #         add_chirp_tag_to_db = ChirpTag.create_chirp_tag(cls, chirp_id, tag.id)
    #         return 'added'
    #     else:
    #         return 'not added'
