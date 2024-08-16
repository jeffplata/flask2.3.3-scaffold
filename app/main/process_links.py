# process_links
from app.main import bp
from flask import jsonify, request, abort
from sqlalchemy import select, func, String
from sqlalchemy.exc import IntegrityError
from app.model_classes import get_model_class, is_one_to_many
from app import db

def get_parent_child_models(subpath):
    path_segments = subpath.split('/')
    parent_children = path_segments[0].split('_')
    if len(parent_children) < 2:
        raise ValueError("Invalid parent-child specification in URL.")
    
    parent_model_class = get_model_class(parent_children[0])
    child_model_class = get_model_class(parent_children[1])

    return parent_model_class, child_model_class, parent_children[1]

def get_parent_child_instances(parent_model, child_model):
    parent_id = request.args.get('parent_id')
    child_id = request.args.get('child_id')
    if not parent_id or not child_id:
        raise ValueError("Missing parent_id or child_id in args")
    
    parent_instance = parent_model.query.get(int(parent_id))
    child_instance = child_model.query.get(int(child_id))
    if not parent_instance or not child_instance:
        raise ValueError("Parent or child instance not found")
    
    return parent_instance, child_instance

def safe_icontains_filter(model, search_term, columns_to_return=['id', 'name']):
    filters = []
    columns = []
    for col_name in columns_to_return:
        column = getattr(model, col_name)
        columns.append(column)
        if isinstance(column.type, String):
            filters.append(func.lower(column).like(f'%{search_term.lower()}%'))
    
    if not filters:
        return select(*columns).where(False)
    
    return select(*columns).where(db.or_(*filters))

@bp.route('/links/<path:subpath>/<string:action>/', methods=['GET', 'POST'])
def process_links(subpath='', action=None):
    try:
        parent_model, child_model, relationship_name = get_parent_child_models(subpath)
        
        if action == 'get':
            parent_id = request.args.get('parent_id')
            parent_instance = parent_model.query.get(int(parent_id))
            dataset = getattr(parent_instance, relationship_name)
            
            start = int(request.args.get('start'))
            limit = int(request.args.get('limit'))
            fn = request.args.get('linkFields').split(',')
            
            totalRows = len(dataset)
            pagedDataset = dataset[start:limit+start]
            pagedDataset_dict = [{f: getattr(d, f) for f in fn} for d in pagedDataset]
            return jsonify({'data': pagedDataset_dict, 'totalRows': totalRows})
        
        elif action in ['new', 'delete']:
            parent_instance, child_instance = get_parent_child_instances(parent_model, child_model)
            relationship_prop = getattr(parent_instance, relationship_name)
            
            if action == 'new':
                if is_one_to_many(parent_model, relationship_name) and child_instance in relationship_prop:
                    return jsonify({'result': 'failed', 'message': 'Duplicate entry.'})
                relationship_prop.append(child_instance)
                message = f"{str(child_instance)} successfully added to {str(parent_instance)}"
            else:  # delete
                if child_instance in relationship_prop:
                    relationship_prop.remove(child_instance)
                message = f"{str(child_instance)} successfully removed from {str(parent_instance)}"
            
            db.session.commit()
            fn = request.args.get('linkFields').split(',') if action == 'new' else ''
            data = {f: getattr(child_instance, f) for f in fn} if action == 'new' else {}
            return jsonify({'result': 'ok', 'message': message, 'data': data})
        
        elif action == 'lookup':
            searchText = request.args.get('searchText')
            fn = request.args.get('linkFields').split(',')
            
            stmt = safe_icontains_filter(child_model, searchText, fn)
            dataset = db.session.execute(stmt).all()
            print(dataset)
            totalRows = len(dataset)
            # dataset_json = [dict(zip(fn, data)) for data in dataset[:10]]
            dataset_json = [{'id': data[0], 'name': data[1]} for data in dataset[:10]]
            return jsonify({'data': dataset_json, 'totalRows': totalRows})
        
        else:
            raise ValueError('Invalid action.')
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'result': 'failed', 'message': 'Duplicate entry'})
    except Exception as e:
        db.session.rollback()
        raise e
        # return jsonify({'result': 'failed', 'message': str(e)})