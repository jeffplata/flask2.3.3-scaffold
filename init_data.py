from app import create_app, db
from app.models import User, Role
from app import Config
import pandas as pd
from app.models2 import Region, Branch, Warehouse, Province
from sqlalchemy import func


app = create_app()

def create_admin():
    with app.app_context():
        role_admin = Role.query.filter_by(name='admin').first()
        if not role_admin:
            role_admin = Role(name='admin', description='admin')
            db.session.add(role_admin)
            db.session.commit()

        user_admin = User.query.filter_by(email='admin@email.com').first()
        if not user_admin:
            user_admin = User(username='admin', email='admin@email.com')
            user_admin.set_password(Config.DEFAULT_PASS)
            db.session.add(user_admin)
            db.session.commit()

        if not user_admin.has_role('admin'):
            user_admin.roles.append(role_admin)
            db.session.commit()

def populate_locations():
    excel_file = 'nfa inventory app data bsmo.xlsx'
    # regions
    if not db.session.query(func.count(Region.id)).scalar():
        selected_sheet = 'regions'
        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        data = df.to_dict('records')

        for r in data:
            reg = Region(name=r['name'], description=r['description'])
            db.session.add(reg)
        db.session.commit()
        print('Regions populated')
    else:
        print('Regions already populated')

    # branches
    if not db.session.query(func.count(Branch.id)).scalar():
        selected_sheet = 'branches'
        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        data = df.to_dict('records')
        
        for r in data:
            bra = Branch(name=r['name'], region_id=r['region_id'])
            db.session.add(bra)
        db.session.commit()
        print('Branches populated')
    else:
        print('Branches already populated')

    # warehouses
    if not db.session.query(func.count(Warehouse.id)).scalar():
        selected_sheet = 'warehouses'
        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        data = df.to_dict('records')
        
        for r in data:
            bra = Warehouse(name=r['name'], location=r['location'], branch_id=r['branch_id'])
            db.session.add(bra)
        db.session.commit()
        print('Warehouses populated')
    else:
        print('Warehouses already populated')

    # provinces
    if not db.session.query(func.count(Province.id)).scalar():
        selected_sheet = 'provinces'
        df = pd.read_excel(excel_file, sheet_name=selected_sheet)
        data = df.to_dict('records')
        
        for r in data:
            prov = Province(name=r['name'])
            db.session.add(prov)
        db.session.commit()
        print('Provinces populated')
    else:
        print('Provinces already populated')


# Uncomment for automatic execution 

# if __name__ == "__main__":
#     create_admin()
#     populate_locations()
