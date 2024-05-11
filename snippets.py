from flask import request, jsonify
from app.api import api_bp
from app.models import User, Role
from app import db
from app.main.forms import UserForm, RoleForm


def apply_filters(query, model, filters):
    filter_conditions = []
    for field, value in filters.items():
        if hasattr(model, field):
            filter_conditions.append(getattr(model, field).contains(value))
    if filter_conditions:
        query = query.filter(db.or_(*filter_conditions))
    return query


def apply_sort(query, model, sort_by, descending):
    if sort_by and hasattr(model, sort_by):
        col = getattr(model, sort_by)
        if descending:
            col = col.desc()
        query = query.order_by(col)
    return query


def paginate(query, start, limit):
    total_rows = query.count()
    query = query.offset(start).limit(limit)
    return query, total_rows


def process_form_data(data, model):
    if data['id'] == '-1':  # New record
        instance = model(**data)
        db.session.add(instance)
    else:  # Existing record
        instance = model.query.get(int(data['id']))
        for key, value in data.items():
            setattr(instance, key, value)
    return instance


def delete_instance(instance):
    db.session.delete(instance)
    db.session.commit()


def get_items(model_class, filters, request_args):
    sort_by = request_args.get('sortby')
    descending = request_args.get('sortdesc') == 'true'
    start = request_args.get('start')
    limit = request_args.get('limit')

    query = apply_filters(model_class.query, model_class, filters)
    query = apply_sort(query, model_class, sort_by, descending)
    query, total_rows = paginate(query, start, limit)

    return query, total_rows


def edit_item(data, form_class, model_class, before_commit_callback=None):
    form = form_class(**data)
    if form.validate():
        try:
            item = process_form_data(data, model_class)
            if before_commit_callback:
                before_commit_callback(item, data)
            db.session.commit()
            return jsonify({'result': 'ok', 'newId': item.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'result': 'failed', 'message': 'Error: Your changes cannot be saved.'})
    return jsonify({'result': 'failed', 'errors': form.errors})


def delete_item(model_class, item_id, before_delete_callback=None):
    item = model_class.query.get(item_id)
    if item:
        try:
            if before_delete_callback and before_delete_callback(item):
                return jsonify({'result': 'failed', 'message': 'You are not allowed to delete this record.'})
            db.session.delete(item)
            db.session.commit()
            return jsonify({'result': 'ok'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'result': 'failed', 'message': 'Failed to delete.'})
    return jsonify({'result': 'failed', 'message': 'Record not found.'})

# User management
# ===============

@api_bp.route("/users_init")
def users_init():
    data = {'title': 'user|users', 'name_field': 'username'}
    return data


@api_bp.route("/users")
def users():
    filters = {
        'username': request.args.get('filtertext'),
        'email': request.args.get('filtertext'),
        'first_name': request.args.get('filtertext'),
        'last_name': request.args.get('filtertext')
    }
    fieldnames = ['id', 'username', 'email', 'first_name', 'last_name']
    query, total_rows = get_items(User, filters, request.args)
    data = [u.to_dict() for u in query]
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows})


def user_before_commit_callback(user, data):
    if data['id'] == '-1':
        user.set_password('Password1')

@api_bp.route("/user_edit", methods=['POST'])
def user_edit():
    data = request.json
    return edit_item(data, UserForm, User, user_before_commit_callback)


def user_before_delete_callback(user):
    if user.email == 'admin@email.com':
        return True
    return False


@api_bp.route("/user_delete", methods=['POST'])
def user_delete():
    item_id = request.args.get('id')
    return delete_item(User, item_id, user_before_delete_callback)

# Role management
# ===============

@api_bp.route("/roles_init")
def roles_init():
    data = {'title': 'role|roles', 'name_field': 'name'}
    return data


@api_bp.route("/roles")
def roles():
    filters = {'name': request.args.get('filtertext'), 'description': request.args.get('filtertext')}
    fieldnames = ['id', 'name', 'description']
    query, total_rows = get_items(Role, filters, request.args)
    data = [{'id': r.id, 'name': r.name, 'description': r.description} for r in query]
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows})


@api_bp.route("/role_edit", methods=['POST'])
def role_edit():
    data = request.json
    return edit_item(data, RoleForm, Role)


def role_before_delete_callback(role):
    if role.name == 'admin':
        return True
    return False


@api_bp.route("/role_delete", methods=['POST'])
def role_delete():
    item_id = request.args.get('id')
    return delete_item(Role, item_id, role_before_delete_callback)