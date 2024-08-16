from app.main import bp
from flask import render_template, request, jsonify
from flask_login import login_required
from app.common import access_required
from app.models import User
from app import db
from .forms import AddUserForm, EditUserForm
from flask import flash, redirect, url_for
from app.models import Role
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


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

# /role_users/
# @bp.route('/role_users/<string:action>/', methods=['GET', 'POST'])
# @bp.route('/role_users/<string:action>/<string:id>', methods=['GET', 'POST'])
# def role_users(action=None, id=None):
#     if action == 'get':
#         data = {}
#         pagedDataset_dict = []
#         start = int(request.args.get('start'))
#         limit = int(request.args.get('limit'))
#         fn = request.args.get('fields').split(',')
#         dataset = Role.query.get(id).users
#         totalRows = len(dataset)
#         pagedDataset = dataset[start:limit+start]
#         pagedDataset_dict = [{f: getattr(d, f) for f in fn} for d in pagedDataset]
#         return jsonify({'data': pagedDataset_dict,'totalRows':totalRows})
#     elif action == 'new':
#         try:
#             parent = Role.query.get(id)
#             child = User.query.get( int(request.args.get('id')) )
#             parent.users.append(child)
#             db.session.commit()
#             fn = request.args.get('linkFields').split(',')
#             data = {f: getattr(child,f) for f in fn}
#             # data = {'id':user.id,'username':user.username,'email':user.email}
#             return jsonify({'result':'ok',
#                             'message':f"Role '{parent.name}' successfully granted to user '{child.username}'",
#                             'data':data})
#         except IntegrityError as e:
#             db.session.rollback()
#             return jsonify({'result':'failed', 'message': 'Duplicate entry'})
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'result':'failed', 'message': e.args[0]})
#     elif action == 'delete': 
#         try:
#             role = Role.query.get(id)
#             user = User.query.get( int(request.args.get('id')) )
#             role.users.remove(user)
#             db.session.commit()
#             # print('delete staged.')
#             return jsonify({'result':'ok','message':f"Role '{role.name}' successfully revoked from user '{user.username}'"})
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({'result':'failed', 'message': e.args[0]})
#     elif action == 'lookup':
#         searchText = request.args.get('searchText').lower()
#         dataset = User.query.filter(db.or_(func.lower(User.username).contains(searchText)))
#         totalRows = dataset.count()
#         dataset_json = [{'id': data.id, 'name': data.username} for data in dataset[:10]]
#         return jsonify({'data':dataset_json,'totalRows':totalRows})
#     else:
#         raise Exception('Invalid action.')
    # return jsonify(data)


@bp.route('/users')
@access_required('admin')
def users():
    roles_dict = [r.to_dict() for r in Role.query]
    return render_template('users_vue.html', allroles=roles_dict)


# @bp.route('/users_load')
# @access_required('admin')
# def users_load():
#     return render_template('1.html')


# @bp.route('/api/user_data')
# @access_required('admin')
# def user_data():
#     query = User.query

#     # search filter
#     search = request.args.get('search[value]')
#     if search:
#         query = query.filter(db.or_(
#             User.username.contains(f'{search}'),
#             User.email.contains(f'{search}'),
#             User.first_name.contains(f'{search}'),
#             User.last_name.contains(f'{search}')
#         ))
#     total_filtered = query.count()

#     # sort
#     order = []
#     i = 0
#     while True:
#         col_index = request.args.get(f'order[{i}][column]')
#         if col_index is None:
#             break
#         col_name = request.args.get(f'columns[{col_index}][data]')
#         if col_name not in ['username', 'email', 'first_name', 'last_name']:
#             col_name = 'username'
#         descending = request.args.get(f'order[{i}][dir]') == 'desc'
#         col = getattr(User, col_name)
#         if descending:
#             col = col.desc()
#         order.append(col)
#         i += 1
#     if order:
#         query = query.order_by(*order)

#     # pagination
#     start = request.args.get('start', type=int)
#     length = request.args.get('length', type=int)
#     query = query.offset(start).limit(length)

#     # response
#     return {
#         'data': [user.to_dict() for user in query],
#         'recordsFiltered': total_filtered,
#         'recordsTotal': User.query.count(),
#         'draw': request.args.get('draw', type=int),
#     }


# @bp.route('/user_add', methods=['GET', 'POST'])
# @access_required('admin')
# def user_add():
#     form = AddUserForm()
#     if request.method == 'POST':
#         print('post')
#         if form.cancel.data:
#             print('cancelled')
#             next_url = request.args.get('next')
#             if next_url:
#                 return redirect(next_url)
#             return redirect(url_for('main.index'))
#         elif form.validate_on_submit():
#             new_user = User(username=form.username.data,
#                         email=form.email.data,
#                         first_name=form.first_name.data,
#                         last_name=form.last_name.data)
#             new_user.set_password('Password2')
#             db.session.add(new_user)
#             db.session.commit()
#             flash('New user added.')
#             return redirect(url_for('main.users'))
#     return render_template('user_add.html', title='Add new user', form=form)


# @bp.route('/user_edit/<id>', methods=['GET', 'POST'])
# @access_required('admin')
# def user_edit(id):
#     user = User.query.get_or_404(id)
#     form = EditUserForm()
#     if request.method == 'POST' and form.cancel.data:
#         next_url = request.args.get('next')
#         if next_url:
#             return redirect(next_url)
#         return redirect(url_for('main.index'))
#     elif form.validate_on_submit():
#         user.username = form.username.data
#         user.first_name = form.first_name.data
#         user.last_name = form.last_name.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#     elif request.method == 'GET':
#         form.username.data = user.username
#         form.email.data = user.email
#         form.first_name.data = user.first_name
#         form.last_name.data = user.last_name
#     return render_template('user_edit.html', title=f'Edit user {user.username}', form=form)
