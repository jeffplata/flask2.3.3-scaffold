from urllib.parse import urlparse

@bp.route('/links/<path:subpath>', methods=['GET', 'POST'])
def handle_links(subpath):
    full_url = urlparse(request.url)
    path_segments = full_url.path.split('/')
    
    if len(path_segments) < 3:
        return "Invalid URL structure", 400

    parent_children = path_segments[2].split('_')
    if len(parent_children) != 2:
        return "Invalid parent-child specification in URL", 400

    try:
        parent_model_class = get_model_class(parent_children[0])
        child_model_class = get_model_class(parent_children[1])
    except ValueError as e:
        return str(e), 400

    # Assume 'id' is passed as a query parameter for both parent and child
    parent_id = request.args.get('parent_id')
    child_id = request.args.get('child_id')

    if not parent_id or not child_id:
        return "Missing parent_id or child_id", 400

    parent_instance = parent_model_class.query.get(int(parent_id))
    child_instance = child_model_class.query.get(int(child_id))

    if not parent_instance or not child_instance:
        return "Parent or child not found", 404

    relationship_name = parent_children[1]  # This might need to be more flexible
    relationship_prop = getattr(parent_instance, relationship_name, None)

    if relationship_prop is None:
        return f"Relationship {relationship_name} not found on {parent_children[0]}", 400

    one_to_many = is_one_to_many(parent_model_class, relationship_name)
    
    if one_to_many:
        if child_instance in relationship_prop:
            # Your logic for when the child is in the relationship
            pass
        else:
            # Your logic for when the child is not in the relationship
            pass
    else:
        # Your logic for many-to-many relationships
        pass

    # Rest of your function logic...
    return "Processed successfully"


# /branch_provinces/
@bp.route('/branch_provinces/<string:action>/', methods=['GET', 'POST'])
@bp.route('/branch_provinces/<string:action>/<string:id>', methods=['GET', 'POST'])
def branch_provinces(action=None, id=None):
    if action == 'get':
        data = {}
        pagedDataset_dict = []
        start = int(request.args.get('start'))
        limit = int(request.args.get('limit'))
        fn = request.args.get('fields').split(',')
        dataset = Branch.query.get(id).provinces
        totalRows = len(dataset)
        pagedDataset = dataset[start:limit+start]
        pagedDataset_dict = [{f: getattr(d, f) for f in fn} for d in pagedDataset]
        return jsonify({'data': pagedDataset_dict,'totalRows':totalRows})
    
    elif action == 'new':
        try:
            parent = Branch.query.get(id)
            child = Province.query.get( int(request.args.get('id')) )
            # from urllib.parse import urlparse
            # full_url = urlparse(request.url)
            # path_segments = full_url.path.split('/')
            # print('path segments: ',path_segments)
            one_to_many = is_one_to_many(Branch,'provinces')
            if one_to_many:
                if child in parent.provinces:
                    return jsonify({'result':'failed',
                                    'message':'Duplicate entry.'})
            parent.provinces.append(child)
            db.session.commit()
            fn = request.args.get('linkFields').split(',')
            data = {f: getattr(child,f) for f in fn}
            # data = {'id':user.id,'username':user.username,'email':user.email}
            return jsonify({'result':'ok',
                            'message':f"Province '{child.name}' successfully added to branch '{parent.name}'",
                            'data':data})
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'result':'failed', 'message': 'Duplicate entry'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'result':'failed', 'message': e.args[0]})
        
    elif action == 'delete': 
        try:
            parent = Branch.query.get(id)
            child = Province.query.get( int(request.args.get('id')) )
            parent.provinces.remove(child)
            db.session.commit()
            # print('delete staged.')
            return jsonify({'result':'ok','message':f"Province '{child.name}' successfully removed from branch '{parent.name}'"})
        except Exception as e:
            db.session.rollback()
            return jsonify({'result':'failed', 'message': e.args[0]})
    elif action == 'lookup':
        searchText = request.args.get('searchText')
        # dataset = Province.query.filter(db.or_(func.lower(Province.name).icontains(searchText)))
        dataset = Province.query.filter(db.or_(Province.name.icontains(searchText)))
        totalRows = dataset.count()
        dataset_json = [{'id': data.id, 'name': data.name} for data in dataset[:10]]
        return jsonify({'data':dataset_json,'totalRows':totalRows})
    else:
        raise Exception('Invalid action.')