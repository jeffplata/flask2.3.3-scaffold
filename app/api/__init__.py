from flask import Blueprint

api_bp = Blueprint('api_bp', __name__)  # "API Blueprint"

from app.api import routes
# from app.api import routes2
