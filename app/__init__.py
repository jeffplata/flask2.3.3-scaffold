from flask import Flask
from app.config import Config
# from flask_bootstrap import Bootstrap4
from flask_bootstrap import Bootstrap5
from app.common import db
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from logging.handlers import SMTPHandler, RotatingFileHandler
import logging
import os
from flask_wtf.csrf import CSRFProtect

# bootstrap = Bootstrap4()
bootstrap = Bootstrap5()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
csrf = CSRFProtect()


from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def create_app(config_class=Config):
    # app = Flask(__name__)
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    from app.errors import bp as errors_bp
    from app.errors.handlers import forbidden, internal_error, not_found_error
    app.register_blueprint(errors_bp)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(500, internal_error)
    app.register_error_handler(404, not_found_error)

    from app.frontend import frontend_bp
    app.register_blueprint(frontend_bp)
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api_v1')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                # fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=app.config['ADMINS'],
                subject='{appname} Failure'.format(appname=app.config['APP_NAME']),
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/{appname}.log'.format(appname=app.config['APP_NAME']),
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('{appname} startup'.format(appname=app.config['APP_NAME']))

    return app
