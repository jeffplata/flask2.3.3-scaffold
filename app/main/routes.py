from app.main import bp
from flask import render_template
from flask_login import login_required
from app.common import access_required
from app.models import Role


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('first.html')


@bp.route('/explore')
@access_required('admin')
def explore():
    return render_template('explore.html')


@bp.route('/about')
@login_required
def about():
    return render_template('about.html')


@bp.route('/roles')
@access_required('admin')
def roles():
    return render_template('roles_vue.html')


@bp.route('/users')
@access_required('admin')
def users():
    roles_dict = [r.to_dict() for r in Role.query]
    return render_template('users_vue.html', allroles=roles_dict)

