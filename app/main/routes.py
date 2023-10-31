from app.main import bp
from flask import render_template, request
from flask_login import login_required
from app.common import access_required
from app.models import User
from app import db
from .forms import AddUserForm, EditUserForm
from flask import flash, redirect, url_for


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
    return render_template('roles.html')


@bp.route('/users')
@access_required('admin')
def users():
    # users = User.query.all()
    # return render_template('users.html', users=users)

    # return render_template('0.html')
    return render_template('index.html')


@bp.route('/users_load')
@access_required('admin')
def users_load():
    return render_template('1.html')


@bp.route('/api/user_data')
@access_required('admin')
def user_data():
    query = User.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            User.username.contains(f'{search}'),
            User.email.contains(f'{search}'),
            User.first_name.contains(f'{search}'),
            User.last_name.contains(f'{search}')
        ))
    total_filtered = query.count()

    # sort
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['username', 'email', 'first_name', 'last_name']:
            col_name = 'username'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(User, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': User.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@bp.route('/user_add', methods=['GET', 'POST'])
@access_required('admin')
def user_add():
    form = AddUserForm()
    if request.method == 'POST':
        print('post')
        if form.cancel.data:
            print('cancelled')
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('main.index'))
        elif form.validate_on_submit():
            new_user = User(username=form.username.data,
                        email=form.email.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data)
            new_user.set_password('Password2')
            db.session.add(new_user)
            db.session.commit()
            flash('New user added.')
            return redirect(url_for('main.users'))
    return render_template('user_add.html', title='Add new user', form=form)


@bp.route('/user_edit/<id>', methods=['GET', 'POST'])
@access_required('admin')
def user_edit(id):
    user = User.query.get_or_404(id)
    form = EditUserForm()
    if request.method == 'POST' and form.cancel.data:
        next_url = request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.index'))
    elif form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        db.session.commit()
        flash('Your changes have been saved.')
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
    return render_template('user_edit.html', title=f'Edit user {user.username}', form=form)
