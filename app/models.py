from datetime import datetime
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import jwt
from flask import current_app


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # messages_sent = db.relationship('Message',
    #                                 foreign_keys='Message.sender_id',
    #                                 backref='author', lazy='dynamic')
    # messages_received = db.relationship('Message',
    #                                     foreign_keys='Message.recipient_id',
    #                                     backref='recipient', lazy='dynamic')
    # last_message_read_time = db.Column(db.DateTime)
    # notifications = db.relationship('Notification', backref='user',
    #                                 lazy='dynamic')
    # tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
