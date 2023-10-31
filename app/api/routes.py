from app.api import api_bp
from app.models import User
from flask import jsonify, request
from app import db
from app.main.forms import UserForm
import json
from app.models import Role


@api_bp.route("/user_init")  # Blueprints don't use the Flask "app" context. They use their own blueprint's
def init():
    data = {'title': 'user|users'}
    return data


@api_bp.route("/users")
def users():
    query = User.query

    # filter
    filtertext = request.args.get('filtertext')
    if filtertext:
        query = query.filter(db.or_(
            User.username.contains(f'{filtertext}'),
            User.email.contains(f'{filtertext}'),
            User.first_name.contains(f'{filtertext}'),
            User.last_name.contains(f'{filtertext}')
        ))

    #sort
    sortby = request.args.get('sortby')
    if sortby:
        col = getattr(User, sortby)
        descending = request.args.get('sortdesc')
        if descending == 'true':
            col = col.desc()
        query = query.order_by(col)

    # pagination
    start = request.args.get('start')
    limit = request.args.get('limit')
    totalrows = query.count()
    query = query.offset(start).limit(limit)

    fieldnames = ['id', {'key': 'username', 'sortable': 'true'},
                  {'key': 'email', 'sortable': 'true'},
                  {'key': 'first_name', 'sortable': 'true'},
                  {'key': 'last_name', 'sortable': 'true'},
                  ]
    data = list([u.to_dict() for u in query])
    return jsonify({'fieldnames': fieldnames,
                    'data': data,
                    'totalrows': totalrows,
                    })


@api_bp.route("/user_add", methods=['GET', 'POST'])
def user_add():
    message = ''
    data = json.loads(json.dumps(request.json))
    form = UserForm(**data)
    if form.validate():
        if data['id'] == '-1':
            user = User(username=data['username'],
                        email=data['email'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        )
            user.set_password('Password1')
            db.session.add(user)
        else:
            user = User.query.get(int(data['id']))
            user.username = data['username']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
        try:
            db.session.commit()
            newid = user.id
            return jsonify({'result': 'ok', 'newId': newid})
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE' in e.args[0]:
                if 'user.username' in e.args[0]:
                    form.username.errors = ['Please use a different user name.']
                if 'user.email' in e.args[0]:
                    form.email.errors = ['Please use a different email address.']
            else:
                message = 'Error: Your changes cannot be saved.'
            return jsonify({'result': 'failed', 'errors': form.errors, 'message': message})

    return {'result': 'failed',
            'errors': form.errors}


@api_bp.route("/user_delete", methods=['POST'])
def user_delete():
    user = User.query.get(request.args.get('id'))
    if user:
        if user.email == 'admin@email.com':
            return {'result': 'failed', 'message': 'You are not allowed to delete this record.'}
        else:
            try:
                db.session.delete(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return {'result': 'failed', 'message': 'Failed to delete.'}
            return {'result': 'ok'}
    return {'result': 'failed', 'message': 'Record not found.'}


@api_bp.route("/roles_init")
def roles_init():
    data = {'title': 'role|'}
    return data


@api_bp.route("/roles")
def roles():
    query = Role.query

    # filter
    filtertext = request.args.get('filtertext')
    if filtertext:
        query = query.filter(db.or_(
            Role.name.contains(f'{filtertext}'),
            Role.description.contains(f'{filtertext}'),
        ))

    #sort
    sortby = request.args.get('sortby')
    if sortby:
        col = getattr(Role, sortby)
        descending = request.args.get('sortdesc')
        if descending == 'true':
            col = col.desc()
        query = query.order_by(col)

    # pagination
    start = request.args.get('start')
    limit = request.args.get('limit')
    totalrows = query.count()
    query = query.offset(start).limit(limit)

    fieldnames = ['id', {'key': 'name', 'sortable': 'true'},
                  {'key': 'description', 'sortable': 'true'},
                  ]
    data = list([{'id':r.id,
                  'name':r.name, 
                  'description':r.description} for r in query])
    return jsonify({'fieldnames': fieldnames,
                    'data': data,
                    'totalrows': totalrows,
                    })
