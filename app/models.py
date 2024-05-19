from datetime import datetime
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import jwt
from flask import current_app


def insert_unique(session, model, match_criteria, **kwargs):
    """
    Insert a record but ensure that it is unique
    """
    instance = session.query(model).filter_by(**match_criteria).first()
    isInserted = False

    if not instance:
        instance_data = {**match_criteria, **kwargs}
        instance = model(**instance_data)
        session.add(instance)
        session.commit()
        isInserted = True

    return isInserted, instance


user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    first_name = db.Column(db.String(80), index=True)
    last_name = db.Column(db.String(80), index=True)
    password = db.Column(db.String(255))

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship(
        "Role", secondary="user_roles", backref=db.backref("users", lazy="dynamic"))

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
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    # def has_role(self, role):
    #     roles = [r.name for r in self.roles]
    #     return role in roles
    
    def has_role(self, role):
        if isinstance(role, Role):
            return role in self.roles
        if isinstance(role, str):
            return any(r.name == role for r in self.roles)
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

    def to_dict_with_roles(self):
        user_dict = self.to_dict()
        roles_dict = {'roles':[{'id': role.id, 'name': role.name} for role in self.roles]}
        return {**user_dict, **roles_dict}

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
