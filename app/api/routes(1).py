from flask import request, jsonify
from app.api import api_bp
from app.models import User, Role, user_roles
from app import db
from app.main.forms import UserForm, RoleForm
import json
from sqlalchemy.exc import IntegrityError
from app.config import Config


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
        instance.id = None  # let the autoincrement work
        # db.session.add(instance)
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


def get_unique_error_message(error_message,form):
    errors = Config.UNIQUE_FIELDS
    for full_field_name, form_prompt in errors:
        if full_field_name in error_message:
            field_name = full_field_name.split('.')[1]
            form._fields[field_name].errors.append(form_prompt)
    return


def edit_item(data, **kwargs):
    # form_class, model_class, item_instance=None, before_commit_callback=None):
    form_class = kwargs.get('form_class')
    model_class = kwargs.get('model_class')
    item_instance = kwargs.get('item_instance')
    before_commit_callback = kwargs.get('before_commit_callback')

    form = form_class(**data)
    message = 'Please correct errors in the form.'
    if form.validate():
        try:
            # the item instance can be defined at the calling item edit (xxx_edit) function
            # ... or generically built in this function if None is passed
            if not item_instance:
                item_instance = process_form_data(data, model_class)
            if data['id'] == '-1':
                db.session.add(item_instance)
            if before_commit_callback:
                before_commit_callback(item_instance, data)
            db.session.commit()
            return jsonify({'result': 'ok', 'newId': item_instance.id})
        except IntegrityError as e:
            db.session.rollback()
            get_unique_error_message(str(e.orig),form)
            if not form.errors:
                if not message:
                    message = e.args[0]
            return jsonify({'result': 'failed', 'errors': form.errors, 'message': message})
        except Exception as e:
            db.session.rollback()
            return jsonify({'result': 'failed', 'errors': form.errors, 'message': message})        
    return jsonify({'result': 'failed', 'errors': form.errors, 'message': message})


def delete_item(model_class, item_id, **kwargs):
    prevent_delete_callback = kwargs.get('prevent_delete_callback')
    delete_exception_callback = kwargs.get('delete_exception_callback')

    item = model_class.query.get(item_id)
    if item:
        try:
            # prevent_delete_callback must return True to abort delete
            if prevent_delete_callback:
                isAbort, message = prevent_delete_callback(item)
                if isAbort:
                    message = 'You are not allowed to delete this record.' if message == '' else message
                    return jsonify({'result': 'failed', 'message': message})
            db.session.delete(item)
            db.session.commit()
            return jsonify({'result': 'ok'})
        except IntegrityError as e:
            db.session.rollback()
            message = 'This record is in use. Deletion is not allowed.'
            return jsonify({'result': 'failed', 'message': message})
        except Exception as e:
            db.session.rollback()
            message = 'This record cannot be deleted.'
            if delete_exception_callback:
                # send back error message from the callback
                message = delete_exception_callback(e) or message
            return jsonify({'result': 'failed', 'message': message})
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
    # fieldnames = ['id', 'username', 'email', 'first_name', 'last_name']
    fieldnames = ['id', 
                  {'key': 'username', 'sortable': 'true'},
                  {'key': 'email', 'sortable': 'true'},
                  {'key': 'first_name', 'sortable': 'true'},
                  {'key': 'last_name', 'sortable': 'true'},
                  ]
    query, total_rows = get_items(User, filters, request.args)
    data = [u.to_dict_with_roles() for u in query]
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows})


def user_before_commit_callback(user, data):
    if data['id'] == '-1':
        user.set_password('Password1')

# @api_bp.route("/user_edit", methods=['POST'])
# def user_edit():
#     data = request.json
#     return edit_item(data, UserForm, User, user_before_commit_callback)


@api_bp.route("/user_edit", methods=['POST'])
def user_edit():
    data = request.json
    roles_as_js = data.get('roles', '')
    try:
        roles_as_list = json.loads(roles_as_js)
    except:
        roles_as_list = []
    
    if data['id'] == '-1':
        user = User(username=data.get('username', ''),
                    email=data.get('email', ''),
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    )
        user.set_password('Password1')
        # db.session.add(user)
    else:
        user = User.query.get(int(data['id']))
        user.username = data.get('username', '')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')

    res = edit_item(data, 
                    form_class=UserForm, 
                    model_class=User, 
                    item_instance=user)
    if res.json.get('result') == 'ok':
        form_role_ids = [role['id'] for role in roles_as_list]
        db_role_ids = [role.id for role in user.roles]

        roles_to_delete = list(set(db_role_ids) - set(form_role_ids))
        roles_to_add = list(set(form_role_ids) - set(db_role_ids))

        if user.email == 'admin@email.com':
            admin_role = Role.query.filter(Role.name=='admin').first()
            if admin_role and admin_role.id in roles_to_delete:
                return jsonify({'result':'failed','errors':[],'message':"You are not allowed to revoke the 'admin' role for this user." })

        # delete removed roles
        delete_query = user_roles.delete().where(
            (user_roles.c.user_id == user.id) &
            (user_roles.c.role_id.in_(roles_to_delete))
        )
        db.session.execute(delete_query)

        # add new roles
        role_objects_to_add = Role.query.filter(Role.id.in_(roles_to_add)).all()
        user.roles.extend(role_objects_to_add)

        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'result':'failed','errors':[],'message':'Failed to update roles.' })

    return res


def user_prevent_delete_callback(user):
    return user.email == 'admin@email.com', 'You are not allowed to delete this user.'


@api_bp.route("/user_delete", methods=['POST'])
def user_delete():
    item_id = request.args.get('id')
    return delete_item(User, item_id, prevent_delete_callback=user_prevent_delete_callback)


# Role management
# ===============

@api_bp.route("/roles_init")
def roles_init():
    data = {'title': 'role|roles', 'name_field': 'name'}
    return data


@api_bp.route("/roles")
def roles():
    filters = {'name': request.args.get('filtertext'), 'description': request.args.get('filtertext')}
    # fieldnames = ['id', 'name', 'description']
    fieldnames = ['id', {'key':'name', 'sortable': 'true'}, 'description']
    query, total_rows = get_items(Role, filters, request.args)
    data = [{'id': r.id, 'name': r.name, 'description': r.description} for r in query]
    return jsonify({'fieldnames':fieldnames,'data':data,'totalrows':total_rows})


@api_bp.route("/role_edit", methods=['POST'])
def role_edit():
    data = request.json
    if data['id'] != '-1':
        role = Role.query.get(int(data['id']))
        if role.name == 'admin':
            return jsonify({'result':'failed','errors':[],'message':'You are not allowed to edit this record.'})
    return edit_item(data,
                     form_class=RoleForm,
                     model_class=Role,
                     )


def role_prevent_delete_callback(role):
    if role.name == 'admin':
        return True, 'You are not allowed to delete this role.' 
    if role.users.all():
        return True, 'This role is in use. Deletion is not allowed.'
    return False, ''


@api_bp.route("/role_delete", methods=['POST'])
def role_delete():
    item_id = request.args.get('id')
    return delete_item(Role, item_id, role_prevent_delete_callback)