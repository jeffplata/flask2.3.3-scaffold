from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import current_user
from werkzeug.exceptions import Forbidden
from flask import current_app

db = SQLAlchemy()


def access_required(*roles):
    """
    see: https://flask.palletsprojects.com/en/2.1.x/patterns/viewdecorators/
    """

    def wrapper(fn):
        @wraps(fn)
        
        def decorated_view(*args, **kwargs):
            if current_user.is_anonymous:
                return current_app.login_manager.unauthorized()
            user_roles = [r.name for r in current_user.roles]
            if any(role in roles for role in user_roles):
                return fn(*args, **kwargs)
            else:
                raise Forbidden("You do not have access to this resource.")
        return decorated_view
    
        # def decorated_view(*args, **kwargs):
        #     if current_user.is_anonymous:
        #         # next_url = make_next_param(request.url, request.url)
        #         # return redirect(url_for('auth.login', next=next_url))
        #         return current_app.login_manager.unauthorized()
        #     uroles = sorted([r.name for r in current_user.roles])
        #     if len(uroles) >= len(roles):
        #         for r in uroles:
        #             role_found = r in roles
        #             if not role_found:
        #                 raise Forbidden
        #     else:
        #         raise Forbidden
        #     return fn(*args, **kwargs)
        # return decorated_view
        
    return wrapper

