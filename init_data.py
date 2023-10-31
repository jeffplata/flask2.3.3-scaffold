from app import create_app, db
from app.models import User, Role

app = create_app()

with app.app_context():
    role_admin = Role.query.filter_by(name='admin').first()
    if not role_admin:
        role_admin = Role(name='admin', description='admin')
        db.session.add(role_admin)
        db.session.commit()

    user_admin = User.query.filter_by(username='admin').first()
    if not user_admin:
        user_admin = User(username='admin', email='admin@email.com')
        user_admin.set_password('Password13')
        db.session.add(user_admin)
        db.session.commit()

    if not user_admin.has_role('admin'):
        user_admin.roles.append(role_admin)
        db.session.commit()
