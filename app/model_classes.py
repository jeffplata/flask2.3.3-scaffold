from .models import User, Role
from .models2 import Activity, Commodity, Container, Variety, Item, \
    Region, Branch, Province, Warehouse, Accountability
from sqlalchemy.inspection import inspect


models_list = [User, Role, Activity, Commodity, Container, Variety, 
              Item, Region, Branch, Province, Warehouse, Accountability]

# plurals are used in relationship names
models_plurals = ['users', 'roles', 'activities', 'commodities', 'containers', 'varieties', 
              'items', 'regions', 'branches', 'provinces', 'warehouses', 'accountabilities']

base_registry = {model.__name__.lower(): model for model in models_list}
ext_registry = {plural: model for plural, model in zip(models_plurals, models_list)}

model_registry = {**base_registry, **ext_registry}


def get_model_class(model_name):
    model_class = model_registry.get(model_name.lower())
    if model_class is None:
        raise ValueError(f"Model class '{model_name}' not found.")
    return model_class


def is_one_to_many(model_class, relationship_name):
    relationship_prop = getattr(model_class, relationship_name).property
    return relationship_prop.secondary is None

# Helper function to get the primary key of a model
# may be used for ordering if needed
# todo: order by pk id
def get_primary_key(model):
    return inspect(model).primary_key[0]
