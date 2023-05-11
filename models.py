from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import uuid

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    displayname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    def __init__(self, username, displayname, avatar, password):
        self.username = username
        self.displayname = displayname
        self.avatar = avatar
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    @classmethod
    def register(cls, username, displayname, avatar, password):
        user = cls(username, displayname, avatar, password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        else:
            return None

    @classmethod
    def delete_user(self, username, password):
        if self.username == username and bcrypt.check_password_hash(self.password_hash, password):
            db.session.delete(self)
            db.session.commit()
            return True
        else:
            return False