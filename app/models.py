from datetime import datetime, timezone
from time import time
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import jwt
from flask import current_app
from sqlalchemy import event, inspect, UniqueConstraint, func, case
from app import Config
# from .models2 import Accountability
from sqlalchemy.ext.hybrid import hybrid_property


def utc_now():
    return datetime.now(timezone.utc)


class TimestampMixin(object):
    created_on = db.Column(db.DateTime, default=utc_now)
    modified_on = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

class UserTrackingMixin(object):
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    modified_by = db.Column(db.Integer, db.ForeignKey('user.id'))


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
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete='RESTRICT')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id', ondelete='RESTRICT')),
    UniqueConstraint('user_id', 'role_id', name='uq_user_role')
    )



class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255), default='')

    users = db.relationship(
        "User", secondary="user_roles", 
        # backref=db.backref("roles", lazy="dynamic"),
        back_populates='roles',
        passive_deletes='all')
    
    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
    
    def in_use(self):
        return user_roles.query.filter(user_roles.role_id==self.id).first() is not None


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    first_name = db.Column(db.String(80), index=True, default='')
    last_name = db.Column(db.String(80), index=True, default='')
    password = db.Column(db.String(255))

    # last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    # user instance will be deleted regardless of presence of assigned roles
    roles = db.relationship(
        "Role", secondary="user_roles", 
        back_populates='users',)
        # backref=db.backref("users", lazy="dynamic"),
        # passive_deletes='true')

    accountabilities = db.relationship('Accountability', back_populates='warehouse_supervisor')

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
    
    @hybrid_property
    def display_name(self):
        full_name = ', '.join(filter(None,(self.last_name, self.first_name)))
        return full_name or self.username or self.email
    
    @display_name.expression
    def display_name(cls):
        full_name = case(
            (func.coalesce(cls.last_name, '') != '', 
             func.concat(cls.last_name, ', ', cls.first_name)),
            else_=cls.first_name
        )
        
        return case(
            (full_name != '', full_name),
            (cls.username != None, cls.username),
            else_=cls.email
        )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        self_password = self.password if  self.password else ''
        return check_password_hash(self_password, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

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


def is_user_admin(user):
    return user.email == 'admin@email.com'

def is_role_admin(role):
    return role.name == 'admin'


# Define the event listener function
def before_insert_listener(mapper, connection, target):
    if isinstance(target, User) and not target.password:
        target.set_password(Config.DEFAULT_PASS)

def before_delete_listener(mapper, connection, target):
    if isinstance(target, User):
        if target.email == 'admin@email.com':
            raise ValueError('You are not allowed to delete this user.')
        if current_user.is_authenticated and (target.id == current_user.id):
            raise ValueError('You are not allowed to delete the currently logged-in user.')
    elif isinstance(target, Role):
        if target.name == 'admin':
            raise ValueError('You are not allowed to delete this role.')
        
def before_update_listener(mapper, connection, target):
    if isinstance(target, User) and target.email == 'admin@email.com':
        history = inspect(target).get_history('username', False)
        if history.has_changes():
            old_username = history.deleted[0]
        else:
            old_username = target.username
        if old_username != target.username:
            raise ValueError('You are not allowed to change the username of this user.')

# Attach the listener to the User model
event.listen(User, 'before_insert', before_insert_listener)
event.listen(User, 'before_update', before_update_listener)
event.listen(User, 'before_delete', before_delete_listener)
event.listen(Role, 'before_delete', before_delete_listener)


@event.listens_for(User.roles, 'remove')
def before_delete_user_roles(target, value, initiator):
    errored = is_user_admin(target) and is_role_admin(value)
    if errored:
        raise ValueError("The 'admin' role cannot be revoked from the 'admin' user.")

@event.listens_for(Role.users, 'remove')
def before_delete_role_users(target, value, initiator):
    errored = is_user_admin(value) and is_role_admin(target)
    if errored:
        raise ValueError("The 'admin' role cannot be revoked from the 'admin' user.")
