from flask import Blueprint
import os

# if serving vue-compiled pages
# template_folder = os.path.join(os.getcwd(), "app", "dist")
# template_folder = template_folder.replace("\\", "/")
# static_url_path = '/app/dist'

# if serving jinja/flask templates with vue js
template_folder = None
static_folder = None
static_url_path = None

frontend_bp = Blueprint("frontend_bp", __name__,  # 'Client Blueprint'
                        template_folder=template_folder,  # Required for our purposes
                        static_folder=static_folder,  # Again, this is required
                        static_url_path=static_url_path  # Flask will be confused if you don't do this
                        )

from app.frontend import routes
