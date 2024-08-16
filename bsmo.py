from app import create_app, db
from app.models import User, Role, user_roles
from app.models2 import Commodity, Container, Variety
import app.models2
from init_data import create_admin, populate_locations

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'user_roles': user_roles,
            'Commodity': Commodity, 'Container': Container, 'Variety': Variety,
            'create_admin': create_admin,
            'populate_locations': populate_locations,}

