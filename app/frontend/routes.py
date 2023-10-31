from app.frontend import frontend_bp
from flask import render_template
import os
from flask import send_from_directory


DIST_DIR = os.path.join(os.getcwd(), 'app', 'dist')


@frontend_bp.route("/main")
def main():
    return render_template("frontend/index.html")
    # return render_template("index.html")
    
    # when serving from vue-built sources
    # return send_from_directory(DIST_DIR, 'index.html')


@frontend_bp.route('/<path:path>')
def static_proxy(path):
    file_name = path.split('/')[-1]
    dir_name = os.path.join(DIST_DIR, '/'.join(path.split('/')[:-1]))
    return send_from_directory(dir_name, file_name)
