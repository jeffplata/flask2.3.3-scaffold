from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import redirect, url_for, request
from flask_login import current_user
from werkzeug.exceptions import Forbidden

db = SQLAlchemy()


def access_required(*roles):
    """
    see: https://flask.palletsprojects.com/en/2.1.x/patterns/viewdecorators/
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if current_user.is_anonymous:
                return redirect(url_for('auth.login', next=request.url))
            uroles = sorted([r.name for r in current_user.roles])
            if len(uroles) >= len(roles):
                for r in uroles:
                    role_found = r in roles
                    if not role_found:
                        raise Forbidden
            else:
                raise Forbidden
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
