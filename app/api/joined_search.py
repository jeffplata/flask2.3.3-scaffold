from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from sqlalchemy.inspection import inspect
from app.model_classes import get_model_class


FIELD_RELATIONSHIP_REGISTRY = {}


def get_relationship_for_model(base_model, target_model_name):
    mapper = inspect(base_model)
    for rel in mapper.relationships:
        if rel.mapper.class_.__name__.lower() == target_model_name.lower():
            return rel.key
    return None


def get_relationships_for_fields(table, filter_fields):
    table_class = get_model_class(table)
    
    relationships = set()

    if table not in FIELD_RELATIONSHIP_REGISTRY:
        FIELD_RELATIONSHIP_REGISTRY[table] = {}

    for field in filter_fields:
        if field not in FIELD_RELATIONSHIP_REGISTRY[table]:
            if '.' in field:
                model_name, _ = field.split('.')
                if model_name.lower() != table.lower():
                    rel = get_relationship_for_model(table_class, model_name)
                    FIELD_RELATIONSHIP_REGISTRY[table][field] = rel
        
        rel = FIELD_RELATIONSHIP_REGISTRY[table].get(field)
        if rel:
            relationships.add(rel)
    
    return list(relationships)


def compound_search(table, filter_fields, search_text):
    table_class = get_model_class(table)
    search_text = f"%{search_text.lower()}%"

    relationships_to_load = get_relationships_for_fields(table, filter_fields)

    joinedload_options = [joinedload(getattr(table_class, rel)) for rel in relationships_to_load]

    joins = [getattr(table_class, rel) for rel in relationships_to_load]

    filters = []
    for field in filter_fields:
        if '.' in field:
            model_name, attr_name = field.split('.')
        else:
            model_name = table
            attr_name = field
        model_class = get_model_class(model_name)
        filters.append(func.lower(getattr(model_class, attr_name)).like(search_text))

    query = table_class.query.options(*joinedload_options)

    for join in joins:
        query = query.join(join)

    query = query.filter(or_(*filters))

    # return query.all()
    return query


# # Example usage:
# found_list_acc = js.compound_search(
#     'Accountability',
#     ['warehouse_supervisor', 'warehouse'],
#     ['Accountability.name', 'User.username', 'User.email', 'Warehouse.name'],
#     'adm'
# )

# found_list_var = compound_search(
#     'Variety',
#     ['commodity'],
#     ['Variety.name', 'Commodity.name'],
#     'palay'
# )

# def compound_search_table(table, relationships, filter_fields, search_text, page=1, per_page=20):
#     # ... (previous code) ...

#     query = query.filter(or_(*filters))

#     # Apply pagination
#     paginated = query.paginate(page=page, per_page=per_page, error_out=False)

#     return paginated.items, paginated.total