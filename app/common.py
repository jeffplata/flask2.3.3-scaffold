from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import current_user
from werkzeug.exceptions import Forbidden
from flask import current_app

db = SQLAlchemy()


def access_required(roles):
    """
    see: https://flask.palletsprojects.com/en/2.1.x/patterns/viewdecorators/
    """

    def wrapper(fn):
        @wraps(fn)
        
        def decorated_view(*args, **kwargs):
            if current_user.is_anonymous:
                return current_app.login_manager.unauthorized()
            user_roles = [r.name for r in current_user.roles]
            # print(roles)
            # print(user_roles)
            if any(role in roles for role in user_roles):
                return fn(*args, **kwargs)
            else:
                raise Forbidden("You do not have access to this resource.")
        return decorated_view
        
    return wrapper
