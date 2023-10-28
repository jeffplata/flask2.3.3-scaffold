from app.main import bp
from flask import render_template
from flask_login import login_required
from app.common import access_required


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html')


@bp.route('/explore')
@access_required('admin')
def explore():
    return render_template('explore.html')


@bp.route('/about')
def about():
    return render_template('about.html')



