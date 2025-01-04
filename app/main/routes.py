from app.main import bp
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.common import access_required
from app.models import Role
from app.models2 import Accountability


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


@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.has_role('admin'):
        return redirect(url_for('main.dashboard_admin'))
    elif current_user.has_role('ws'):
        return redirect(url_for('main.dashboard_ws'))
    return redirect(url_for('main.index'))
    

@bp.route('/dashboard_admin')
@access_required('admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')
    

@bp.route('/dashboard_ws')
@access_required('ws')
def dashboard_ws():
    accountabilities = Accountability.query.filter_by(ws_id=current_user.id)
    return render_template('dashboard_ws.html', accountabilities=accountabilities)
